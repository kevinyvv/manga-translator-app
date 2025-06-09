"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { UploadSection } from "@/components/upload-section"
import { LanguageSelector } from "@/components/language-selector"
import { ProcessingStatus } from "@/components/processing-status"
import { ResultsDisplay } from "@/components/results-display"
import { FeatureCards } from "@/components/feature-cards"

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [sourceLanguage, setSourceLanguage] = useState("ja")
  const [targetLanguage, setTargetLanguage] = useState("en")
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [results, setResults] = useState<any[]>([])

  const handleFilesUpload = (files: File[]) => {
    setUploadedFiles(files)
    setResults([])
  }


  const handleTranslate = async () => {
    if (uploadedFiles.length === 0) return

    setIsProcessing(true)
    setProcessingProgress(0)

    try {
      const formData = new FormData()
      uploadedFiles.forEach((file) => {
        formData.append("image", file)
      })

      const response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        // Convert base64 image to data URL for <img> tag
        const imageUrl = `data:image/png;base64,${data.image}`

         setProcessingProgress(100)
          setIsProcessing(false)

          const resultsArray = data.map((item: any, idx: number) => ({
            id: idx,
            originalFile: uploadedFiles[idx],
            originalUrl: URL.createObjectURL(uploadedFiles[idx]),
            translatedUrl: `data:image/png;base64,${item.image}`,
            detectedText: item.translated_data?.map((t: any) => t.text) || ["No text detected"],
            translatedText: item.translated_data?.map((t: any) => t.translated_text) || ["No text translated"],
          }))

          setResults(resultsArray)
      } else {
        setIsProcessing(false)
        setProcessingProgress(0)
      }
    } catch (error) {
      console.error("Error translating images:", error)
      setIsProcessing(false)
      setProcessingProgress(0)
    }
  }



  useEffect(() => {
    // test api endpoint at 127.001:5000/api/hello
    const testApiEndpoint = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/hello")
        if (!response.ok) {
          throw new Error("Network response was not ok")
        }
        const data = await response.json()
        console.log("API Test Response:", data)
      } catch (error) {
        console.error("Error testing API endpoint:", error)
      }
    }
    testApiEndpoint()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">Manga Auto Translator</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Instantly translate manga pages with AI-powered text detection and translation. Preserve the original layout
            while making content accessible in any language.
          </p>
        </div>

        {/* Main Interface */}
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Upload Section */}
          <UploadSection onFilesUpload={handleFilesUpload} uploadedFiles={uploadedFiles} />

          {/* Language Selection */}
          {uploadedFiles.length > 0 && (
            <LanguageSelector
              sourceLanguage={sourceLanguage}
              targetLanguage={targetLanguage}
              onSourceChange={setSourceLanguage}
              onTargetChange={setTargetLanguage}
              onTranslate={handleTranslate}
              isProcessing={isProcessing}
            />
          )}

          {/* Processing Status */}
          {isProcessing && <ProcessingStatus progress={processingProgress} />}

          {/* Results Display */}
          {results.length > 0 && !isProcessing && <ResultsDisplay results={results} />}
        </div>

        {/* Features Section */}
        {uploadedFiles.length === 0 && <FeatureCards />}
      </main>
    </div>
  )
}
