"use server"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"

export async function addExpenseType(form:FormData){
 await assertPanelSession()
 const name=String(form.get("name")||"").trim().slice(0,90)
 if(name.length<2)throw new Error("Enter a category name.")
 const sql=sqlClient()
 await sql`insert into booking_expense_types(name) values(${name})
 on conflict(name) do update set active=true`
 revalidatePath("/cash-management")
}
export async function recordExpense(form:FormData){
 await assertPanelSession()
 const sql=sqlClient()
 const categoryId=String(form.get("typeId")||"")
 const description=String(form.get("description")||"").trim().slice(0,140)
 const payee=String(form.get("payee")||"").trim().slice(0,120)
 const amount=Number(form.get("amount"))
 const method=String(form.get("method")||"efectivo")
 if(!/^[0-9a-f-]{36}$/.test(categoryId)||description.length<3||!Number.isInteger(amount)||amount<=0||amount>100000000)
  throw new Error("Invalid expense details")
 if(!["efectivo","transferencia","debito","credito","mercadopago"].includes(method))throw new Error("Invalid payment method")
 await sql.begin(async tx=>{
  const types=await tx`select id from booking_expense_types where id=${categoryId} and active=true`
  if(!types.length)throw new Error("Expense category not found")
  const records=await tx`insert into expenses(category,description,amount,method,paid_at)
    values('otros',${description},${amount},${method},now()) returning id`
  await tx`insert into booking_expense_details(expense_id,expense_type_id,payee) values
   (${String(records[0].id)},${categoryId},${payee||null})`
 })
 revalidatePath("/cash-management");revalidatePath("/caja");revalidatePath("/analytics");revalidatePath("/finanzas")
}
export async function recordCashMovement(form:FormData){
 await assertPanelSession()
 const sql=sqlClient()
 const direction=String(form.get("direction")||"")
 const amount=Number(form.get("amount"))
 const recipient=String(form.get("recipient")||"").trim().slice(0,120)
 const note=String(form.get("note")||"").trim().slice(0,250)
 if(!["deposit","withdrawal"].includes(direction)||!Number.isInteger(amount)||amount<=0||amount>100000000)
  throw new Error("Invalid cash movement")
 await sql`insert into booking_cash_movements(direction,amount,recipient,note)
 values(${direction},${amount},${recipient||null},${note||null})`
 revalidatePath("/cash-management");revalidatePath("/analytics")
}
