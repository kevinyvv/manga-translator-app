import { Languages, Github, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Languages className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">MangaTranslate</span>
          </div>

          <nav className="hidden md:flex items-center space-x-6">
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
              How it Works
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
              Supported Languages
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
              API
            </a>
          </nav>

          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon">
              <Github className="h-5 w-5" />
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
