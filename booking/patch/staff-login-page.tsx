import Link from "next/link"
import { StaffLoginForm } from "./form"
export const metadata={title:"Staff sign in"}
export default function StaffLoginPage(){
 return <main className="flex min-h-dvh items-center justify-center bg-obsidian px-5 text-ivory">
  <section className="w-full max-w-sm rounded-3xl border border-line-strong bg-surface-1 p-6">
   <div className="mb-6 grid size-14 place-items-center rounded-2xl bg-surface-3 text-2xl">✂</div>
   <h1 className="text-2xl font-bold">Staff sign in</h1>
   <p className="mt-2 text-sm text-ivory-3">Use the credentials provided by your manager.</p>
   <StaffLoginForm/>
   <Link href="/login" className="mt-6 block text-center text-sm text-ivory-3 underline underline-offset-4">Administrator sign in</Link>
  </section>
 </main>
}
