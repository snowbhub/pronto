"use client"
import dynamic from "next/dynamic"
import type { ComponentProps } from "react"
import type { ClientsView } from "./clients-view"

type Props = ComponentProps<typeof ClientsView>

const Directory = dynamic(
  () => import("./clients-view").then(module => module.ClientsView),
  {
    ssr: false,
    loading: () => (
      <div className="mt-4 space-y-2" role="status" aria-label="Loading client list">
        <div className="h-12 animate-pulse rounded-xl border border-line bg-surface-2" />
        <div className="h-14 animate-pulse rounded-xl border border-line bg-surface-2" />
        <div className="h-14 animate-pulse rounded-xl border border-line bg-surface-2" />
      </div>
    ),
  }
)

export function ClientDirectory(props: Props) {
  return <Directory {...props} />
}
