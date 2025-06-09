"use client"

import { useState, useEffect, useRef } from "react"
import FOG from "vanta/dist/vanta.fog.min"
import * as THREE from "three"

export const Background = () => {
  const vantaRef = useRef(null)
  const [vantaEffect, setVantaEffect] = useState<any>(null)

  useEffect(() => {
    if (!vantaEffect && vantaRef.current) {
      setVantaEffect(
        FOG({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.0,
          minWidth: 200.0,
          highlightColor: 0xffffff,
          midtoneColor: 0xff6c94,
          lowlightColor: 0xda0443,
          blurFactor: 0.9,
          speed: 2.5,
          zoom: 0.9,
        }),
      )
    }
    return () => {
      if (vantaEffect) vantaEffect.destroy()
    }
  }, [vantaEffect])

  return (
    <div
      ref={vantaRef}
      className="fixed top-0 left-0 w-full h-full -z-10 pointer-events-none"
      style={{ opacity: 0.5 }}
    />
  )
} 