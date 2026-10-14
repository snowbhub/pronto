"use client"
import { useState,useTransition } from "react"
import { staffLogin } from "@/lib/auth/staff-actions"
export function StaffLoginForm(){
 const [error,setError]=useState("")
 const [pending,start]=useTransition()
 return <form className="mt-8 space-y-4" onSubmit={e=>{
   e.preventDefault();setError("")
   const form=new FormData(e.currentTarget)
   start(async()=>{const result=await staffLogin(form);if(result&&!result.ok)setError(result.error)})
 }}>
  <label className="block text-sm font-medium">Username<input name="username" autoComplete="username" required className="mt-2 h-12 w-full rounded-xl border border-line-strong bg-surface-1 px-4 text-base"/></label>
  <label className="block text-sm font-medium">Password<input name="password" type="password" autoComplete="current-password" required className="mt-2 h-12 w-full rounded-xl border border-line-strong bg-surface-1 px-4 text-base"/></label>
  {error&&<p role="alert" className="text-sm text-danger">{error}</p>}
  <button disabled={pending} className="h-12 w-full rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-50">{pending?"Signing in…":"Sign in"}</button>
 </form>
}
