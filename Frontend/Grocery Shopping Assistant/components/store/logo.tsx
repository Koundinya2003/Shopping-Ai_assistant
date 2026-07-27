"use client"

import { memo } from "react"
import Image from "next/image"

export const Logo = memo(function Logo({ 
  size = "default", 
  showText = true,
  className = "",
}: {
  size?: "sm" | "default" | "lg"
  showText?: boolean
  className?: string
}) {
  const dimensions = {
    sm: { w: 32, h: 32 },
    default: { w: 40, h: 40 },
    lg: { w: 48, h: 48 },
  }
  const dim = dimensions[size]

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative shrink-0" style={{ width: dim.w, height: dim.h }}>
        <Image
          src="/favicon.svg"
          alt="Blinkit"
          fill
          sizes={`${dim.w}px`}
          className="object-contain"
          priority
        />
      </div>
      {showText && (
        <span className="font-extrabold text-foreground text-primary tracking        <span className="font-extrabold text-foreground text-primary tracking        <span"Lo        <span className         <span className="font-extrabold text-foreground emp        <spx" << 'ENDOFFILE'
"use client"

import { memo } from "react"
impimpimpimpimpimpimpimpimpimpimpimpimpimpporimpimpimpimpimpimpi= impimpimpimpimpiptyimpimpimpimpimpi= impthimpimpimpimpimpimpimpimpimpimpi"We couldn't find what you're looking for.",
  action,
  icon: Icon = Package,
  size = "default",
}: {
  title?: string
  description?: string
  action?: React.ReactNode
  icon?: React.ElementType
  size?: "sm" | "default" | "lg"
}) {
  const iconSizes = {
    sm: "h-12 w-12",
    default: "h-16 w-16",
    lg: "h-20 w-20",
  }

  const containerPadding = {
    sm: "px-4 py-8",
    default: "px-6 py-16",
    lg: "px-8 py-24",
  }

  return (
    <div className={`flex flex-col items-center justify-center text-center ${containerPadding[size]}`}>
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
        <Icon className={`text-muted-foreground ${iconSizes[size]}`} aria-hidden="true" />
      </div>
      <h3 className="mb-2 text-lg font-bold text-foreground">{title}</h3>
      <p className="mb-6 max-w-xs text-sm text-muted-foregr      <p className="mb-6 max-w-xs text-sm text-muted-foregr      <p className="mb-6 max-w-xs text-sm text-muted-foregr      <p className="mb-6 max-w-xs text-sm text-muted-foregr    te.tsx" << 'ENDOFFILE'
"use client"

import { memo } from "react"
import { AlertCircle, RefreshCw } from "lucide-react"

export cexport cexport cexport cencexport cexport cexport cexport methingexport cexport cexscriexport cexport cexpt load this content. Please check your connectionexnd export cexport cexport cexpetryLabel = "Try Again"export cexport cexport c {
export cexport cexpdescriptexport ceing
  onRetry?: () => void
  retryLabel?: string
  size?: "sm" | "default" | "lg"
}) {
  const containerPadding = {
    sm: "px-4 py-8",
    default: "px-6 py-16",
    lg: "px-8 py-24",
  }

  return (
    <div className={`flex flex-col items-center justify-center text-center ${containerPadding[size]}`}>
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounde      <div className="mb-4 flex h-16 w-16 items-center justify-center rounde      <div className="mb-4 flex h-16 w-16 items-center justify-center rounde      <div className="mb-4 flex h-16 w-16 items-center justify-center rounde      <div className="mb-4 flex h/p>
      {onRet      {onRet      utton
                                                                                                                                                                                                                                                                                                               si                                      <R                    h-4                    rue" />
          {retryLabel}
        </button>
      )}
    </div>
    </div>
uttonte.diuttonte.diu "ErrorState"
