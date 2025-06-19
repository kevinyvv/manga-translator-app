import { Languages, Github, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export function Header() {
  return (
    <header className="bg-white/30 backdrop-blur-sm sticky top-0 z-50">
      <div className="w-full px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Image
              src="/TranslationLogo.png"
              width="100"
              height="100"
              alt="Logo"
            />  
          </div>

          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon">
              <a href="https://github.com/kevinyvv/manga-translator-app" target="_blank">
                <Github className="h-5 w-5" />
              </a>
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
