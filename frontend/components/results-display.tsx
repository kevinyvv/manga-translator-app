"use client"

import { Download, Eye, RotateCcw } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ResultsDisplayProps {
  results: Array<{
    id: number
    originalFile: File
    originalUrl: string
    translatedUrl: string
    detectedText: string[]
    translatedText: string[]
  }>
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
  const downloadAll = () => {
    // In a real app, this would download all translated images
    console.log("Downloading all translated images...")
  }

  return (
    <Card className="bg-white/60">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <span>Translation Results</span>
            <Badge variant="secondary">{results.length} pages</Badge>
          </CardTitle>
          <Button onClick={downloadAll}>
            <Download className="h-4 w-4 mr-2" />
            Download All
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {results.map((result) => (
            <div key={result.id} className="rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-gray-900">{result.originalFile.name}</h4>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                  <Button variant="outline" size="sm">
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
                        src={result.originalUrl || "/placeholder.svg"}
                        alt="Original"
                        className="w-full rounded-lg border"
                      />
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-700 mb-2">Translated</h5>
                      <img
                        src={result.translatedUrl || "/placeholder.svg"}
                        alt="Translated"
                        className="w-full rounded-lg border"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="original" className="mt-4">
                  <img
                    src={result.originalUrl || "/placeholder.svg"}
                    alt="Original"
                    className="w-full max-w-md mx-auto rounded-lg border"
                  />
                </TabsContent>

                <TabsContent value="translated" className="mt-4">
                  <img
                    src={result.translatedUrl || "/placeholder.svg"}
                    alt="Translated"
                    className="w-full max-w-md mx-auto rounded-lg border"
                  />
                </TabsContent>
              </Tabs>

              <div className="mt-4 grid md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">Detected Text</h5>
                  <div className="space-y-1">
                    {result.detectedText.map((text, index) => (
                      <div key={index} className="text-sm bg-gray-100/65 p-2 rounded">
                        {text}
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">Translated Text</h5>
                  <div className="space-y-1">
                    {result.translatedText.map((text, index) => (
                      <div key={index} className="text-sm bg-gray-100/65 p-2 rounded">
                        {text}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
