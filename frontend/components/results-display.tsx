"use client"

import { Download, Eye, RotateCcw, ChevronLeft, ChevronRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState } from "react"

interface ResultsDisplayProps {
  results: Array<{
    id: number
    originalFile: File
    originalUrl: string
    translatedUrl: string
    detectedText: string[]
    translatedText: string[]
  }>,
  handleTranslate: () => void
}

export function 
ResultsDisplay({ results, handleTranslate }: ResultsDisplayProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  
  const downloadAll = () => {
    
    results.forEach((result) => {
      const filename = result.originalFile.name.replace(/\.[^/.]+$/, "") + "-translated.png" // bit iffy on the conversion right now
      downloadFile(result.translatedUrl, filename)
    })
  }

  const downloadFile = (url: string, filename: string) => {
    const link = document.createElement("a")
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }


  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1))
  }

  const goToNext = () => {
    setCurrentIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0))
  }

  if (results.length === 0) {
    return null
  }

  const currentResult = results[currentIndex]

  return (
    <Card className="bg-white/60">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <span>Translation Results</span>
            <Badge variant="secondary">
              {currentIndex + 1}/{results.length}
            </Badge>
          </CardTitle>
          <div className="flex items-center space-x-2">
            {results.length > 1 && (
              <>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={goToPrevious}
                  disabled={results.length <= 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={goToNext}
                  disabled={results.length <= 1}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </>
            )}
            <Button onClick={downloadAll}>
              <Download className="h-4 w-4 mr-2" />
              Download All
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{currentResult.originalFile.name}</h4>
              <div className="flex space-x-2">
                {/* No preview button for now, as users can view images directly in the tabs
                
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-1" />
                  Preview
                </Button> */}
                <Button variant="outline" size="sm" onClick={() => downloadFile(currentResult.originalUrl, currentResult.originalFile.name)}>
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </Button>
                <Button variant="outline" size="sm" onClick={handleTranslate}>
                  <RotateCcw className="h-4 w-4 mr-1" />
                  Retry
                </Button>
              </div>
            </div>

            <Tabs defaultValue="comparison" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="comparison">Comparison</TabsTrigger>
                <TabsTrigger value="original">Original</TabsTrigger>
                <TabsTrigger value="translated">Translated</TabsTrigger>
              </TabsList>

              <TabsContent value="comparison" className="mt-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-gray-700 mb-2">Original</h5>
                    <img
                      src={currentResult.originalUrl || "/placeholder.svg"}
                      alt="Original"
                      className="w-full rounded-lg border"
                    />
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-700 mb-2">Translated</h5>
                    <img
                      src={currentResult.translatedUrl || "/placeholder.svg"}
                      alt="Translated"
                      className="w-full rounded-lg border"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="original" className="mt-4">
                <img
                  src={currentResult.originalUrl || "/placeholder.svg"}
                  alt="Original"
                  className="w-full max-w-md mx-auto rounded-lg border"
                />
              </TabsContent>

              <TabsContent value="translated" className="mt-4">
                <img
                  src={currentResult.translatedUrl || "/placeholder.svg"}
                  alt="Translated"
                  className="w-full max-w-md mx-auto rounded-lg border"
                />
              </TabsContent>
            </Tabs>

            <div className="mt-4 grid md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Detected Text</h5>
                <div className="space-y-1">
                  {currentResult.detectedText.map((text, index) => (
                    <div key={index} className="text-sm bg-gray-100/65 p-2 rounded">
                      {text}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Translated Text</h5>
                <div className="space-y-1">
                  {currentResult.translatedText.map((text, index) => (
                    <div key={index} className="text-sm bg-gray-100/65 p-2 rounded">
                      {text}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Navigation dots for visual feedback */}
          {results.length > 1 && (
            <div className="flex justify-center space-x-2">
              {results.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentIndex 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}