import { sqlClient } from "@/lib/data/store/postgres"
import { PageBody,PageHeader } from "@/components/shell/page-header"
import { saveProduct,updateStock } from "@/lib/inventory/actions"
export const metadata={title:"Inventory"}
export default async function InventoryPage(){
 const sql=sqlClient()
 const products=await sql`select b.*,p.purchase_price,c.name as category
  from booking_stock_balances b join booking_products p on p.id=b.product_id
  left join booking_product_categories c on c.id=p.category_id order by b.name`
 const movements=await sql`select m.quantity_delta,m.reason,m.created_at,p.name
  from booking_stock_movements m join booking_products p on p.id=m.product_id
  order by m.created_at desc limit 15`
 const tr=(en:string,de:string,uk:string)=>en // localized through the instant locale bridge
 return <PageBody className="space-y-5">
   <PageHeader eyebrow="Inventory" title="Products & stock" description="Products, purchases, sales, stock receipts and write-offs."/>
   <div className="grid grid-cols-2 gap-3">
    <div className="panel p-4"><p className="text-xs text-ivory-3">Products</p><p className="mt-1 text-2xl font-semibold">{products.length}</p></div>
    <div className="panel p-4"><p className="text-xs text-ivory-3">Low stock</p><p className="mt-1 text-2xl font-semibold">{products.filter(p=>Number(p.quantity)<=Number(p.reorder_level)).length}</p></div>
   </div>
   <section className="panel space-y-4 p-4">
    <h2 className="font-semibold">New product</h2>
    <form action={saveProduct} className="grid grid-cols-2 gap-3">
     <label className="col-span-2 text-xs text-ivory-2">Product name<input name="name" required minLength={2} maxLength={120} className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="text-xs text-ivory-2">Category<input name="category" placeholder="Hair care" className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="text-xs text-ivory-2">SKU<input name="sku" placeholder="SKU" className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="text-xs text-ivory-2">Sale price<input name="sellPrice" type="number" min={0} required defaultValue={0} className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="text-xs text-ivory-2">Purchase cost<input name="purchasePrice" type="number" min={0} required defaultValue={0} className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="col-span-2 text-xs text-ivory-2">Low stock threshold<input name="reorderLevel" type="number" min={0} defaultValue={3} required className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <button className="col-span-2 min-h-12 rounded-xl bg-ivory font-semibold text-obsidian">Add product</button>
    </form>
   </section>
   <section className="panel space-y-3 p-4">
    <h2 className="font-semibold">Receive / Sell / Write off</h2>
    <form action={updateStock} className="grid grid-cols-2 gap-3">
     <label className="col-span-2 text-xs text-ivory-2">Product<select name="product" required className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base">{products.map(p=><option key={String(p.product_id)} value={String(p.product_id)}>{String(p.name)} — {Number(p.quantity)} in stock</option>)}</select></label>
     <label className="text-xs text-ivory-2">Operation<select name="reason" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"><option value="receipt">Stock receipt</option><option value="sale">Sale</option><option value="writeoff">Write-off</option><option value="return">Return to stock</option></select></label>
     <label className="text-xs text-ivory-2">Quantity<input type="number" name="quantity" min={1} required defaultValue={1} className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="col-span-2 text-xs text-ivory-2">Payment method (for sales)<select name="method" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"><option value="efectivo">Cash</option><option value="transferencia">Bank transfer</option><option value="debito">Debit card</option><option value="credito">Credit card</option></select></label>
     <label className="col-span-2 text-xs text-ivory-2">Note<input name="note" maxLength={300} className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <button disabled={!products.length} className="col-span-2 min-h-12 rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-40">Save operation</button>
    </form>
   </section>
   <section className="panel p-4">
    <h2 className="mb-3 font-semibold">Stock balance</h2>
    <div className="divide-y divide-line">{products.map(p=><div key={String(p.product_id)} className="flex items-center justify-between gap-3 py-3"><div className="min-w-0"><p className="truncate font-medium">{String(p.name)}</p><p className="text-xs text-ivory-3">{String(p.category||"Uncategorized")}{p.sku?" · "+String(p.sku):""}</p></div><div className="text-right"><p className="font-semibold">{Number(p.quantity)} pcs</p><p className="text-xs text-ivory-3">{Number(p.sell_price).toLocaleString("en")} / unit</p></div></div>)}{!products.length&&<p className="py-4 text-sm text-ivory-3">No products yet.</p>}</div>
   </section>
   <section className="panel p-4"><h2 className="mb-3 font-semibold">Recent stock movements</h2><div className="divide-y divide-line">{movements.map((m,i)=><div key={i} className="flex items-center justify-between gap-3 py-2 text-sm"><div><p>{String(m.name)}</p><p className="text-xs text-ivory-3">{String(m.reason)} · {new Date(String(m.created_at)).toLocaleDateString("en-GB")}</p></div><span className="font-semibold">{Number(m.quantity_delta)>0?"+":""}{Number(m.quantity_delta)}</span></div>)}</div></section>
 </PageBody>
}
