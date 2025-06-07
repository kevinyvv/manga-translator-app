"use client"

import { useState } from "react"
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

    // Simulate processing
    const interval = setInterval(() => {
      setProcessingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsProcessing(false)
          // Mock results
          setResults(
            uploadedFiles.map((file, index) => ({
              id: index,
              originalFile: file,
              originalUrl: URL.createObjectURL(file),
              translatedUrl: URL.createObjectURL(file), // In real app, this would be the translated version
              detectedText: ["こんにちは", "元気ですか？", "ありがとう"],
              translatedText: ["Hello", "How are you?", "Thank you"],
            })),
          )
          return 100
        }
        return prev + 10
      })
    }, 500)
  }

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
