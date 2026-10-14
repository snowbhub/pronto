"use server"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"

export async function saveProduct(form: FormData) {
 await assertPanelSession()
 const sql=sqlClient()
 const name=String(form.get("name")||"").trim().slice(0,120)
 const sku=String(form.get("sku")||"").trim().slice(0,60)||null
 const category=String(form.get("category")||"").trim().slice(0,90)
 const sell=Number(form.get("sellPrice"))
 const purchase=Number(form.get("purchasePrice"))
 const reorder=Number(form.get("reorderLevel"))
 if(name.length<2||!Number.isInteger(sell)||sell<0||!Number.isInteger(purchase)||purchase<0||!Number.isInteger(reorder)||reorder<0)throw new Error("Invalid product details")
 await sql.begin(async tx=>{
  let categoryId:string|null=null
  if(category.length>=2){
   const rows=await tx`insert into booking_product_categories(name) values(${category}) on conflict(name) do update set name=excluded.name returning id`
   categoryId=rows[0].id as string
  }
  await tx`insert into booking_products(name,sku,category_id,sell_price,purchase_price,reorder_level)
    values(${name},${sku},${categoryId},${sell},${purchase},${reorder})`
 })
 revalidatePath("/inventory")
}
export async function updateStock(form: FormData) {
 await assertPanelSession()
 const sql=sqlClient()
 const productId=String(form.get("product")||"")
 const reason=String(form.get("reason")||"")
 const amount=Number(form.get("quantity"))
 const note=String(form.get("note")||"").slice(0,300)
 const method=String(form.get("method")||"efectivo")
 if(!/^[0-9a-f-]{36}$/.test(productId)||!Number.isInteger(amount)||amount<=0||amount>100000)throw new Error("Invalid quantity")
 if(!["receipt","sale","writeoff","return"].includes(reason))throw new Error("Invalid stock operation")
 if(!["efectivo","transferencia","debito","credito","mercadopago"].includes(method))throw new Error("Invalid payment method")
 const delta=reason==="sale"||reason==="writeoff"?-amount:amount
 await sql.begin(async tx=>{
  const prod=await tx`select id,name,sell_price,purchase_price from booking_products where id=${productId} and active=true for update`
  if(!prod.length)throw new Error("Product unavailable")
  const balances=await tx`select coalesce(sum(quantity_delta),0)::int as quantity from booking_stock_movements where product_id=${productId}`
  if(Number(balances[0].quantity)+delta<0)throw new Error("Insufficient stock")
  await tx`insert into booking_stock_movements(product_id,quantity_delta,reason,unit_cost,note) values
     (${productId},${delta},${reason},${reason==="receipt"?Number(prod[0].purchase_price):null},${note||null})`
  if(reason==="sale"){
   const price=Number(prod[0].sell_price)*amount
   await tx`insert into payments(concept,kind,list_price,discount,tip,amount,method,units)
      values(${String(prod[0].name)},'producto',${price},0,0,${price},${method},${amount})`
  }
 })
 revalidatePath("/inventory")
 revalidatePath("/caja")
 revalidatePath("/finanzas")
}
