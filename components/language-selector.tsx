"use client"

import { ArrowRight, Play } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface LanguageSelectorProps {
  sourceLanguage: string
  targetLanguage: string
  onSourceChange: (value: string) => void
  onTargetChange: (value: string) => void
  onTranslate: () => void
  isProcessing: boolean
}

const languages = [
  { code: "ja", name: "Japanese", flag: "🇯🇵" },
  { code: "en", name: "English", flag: "🇺🇸" },
  { code: "ko", name: "Korean", flag: "🇰🇷" },
  { code: "zh", name: "Chinese", flag: "🇨🇳" },
  { code: "es", name: "Spanish", flag: "🇪🇸" },
  { code: "fr", name: "French", flag: "🇫🇷" },
  { code: "de", name: "German", flag: "🇩🇪" },
  { code: "pt", name: "Portuguese", flag: "🇵🇹" },
]

export function LanguageSelector({
  sourceLanguage,
  targetLanguage,
  onSourceChange,
  onTargetChange,
  onTranslate,
  isProcessing,
}: LanguageSelectorProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Translation Settings</h3>

        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
            <Select value={sourceLanguage} onValueChange={onSourceChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.code} value={lang.code}>
                    <span className="flex items-center space-x-2">
                      <span>{lang.flag}</span>
                      <span>{lang.name}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-center pt-6">
            <ArrowRight className="h-5 w-5 text-gray-400" />
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
            <Select value={targetLanguage} onValueChange={onTargetChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.code} value={lang.code}>
                    <span className="flex items-center space-x-2">
                      <span>{lang.flag}</span>
                      <span>{lang.name}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button onClick={onTranslate} className="w-full" size="lg" disabled={isProcessing}>
          <Play className="h-4 w-4 mr-2" />
          {isProcessing ? "Processing..." : "Start Translation"}
        </Button>
      </CardContent>
    </Card>
  )
}
