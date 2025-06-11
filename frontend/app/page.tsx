"use client"

import { useState, useEffect, useRef } from "react"
import { Header } from "@/components/header"
import { UploadSection } from "@/components/upload-section"
import { LanguageSelector } from "@/components/language-selector"
import { ProcessingStatus } from "@/components/processing-status"
import { ResultsDisplay } from "@/components/results-display"
import { Background } from "@/components/background"
import Image from "next/image"

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [sourceLanguage, setSourceLanguage] = useState("ja")
  const [targetLanguage, setTargetLanguage] = useState("en")
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [results, setResults] = useState<any[]>([])

  const settingsRef = useRef<HTMLDivElement>(null)

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

  // Scroll to translation settings when files are uploaded
  useEffect(() => {
    if (uploadedFiles.length > 0 && settingsRef.current) {
      settingsRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [uploadedFiles])

  return (
    <div className="min-h-screen relative">
      <Background />
      <Header />

      <main className="container mx-auto px-4 py-64 relative z-10">
        {/* Hero Section */}
        <div className="text-center">
           <Image
              src="/TranslationLogo.png"
              width="400"
              height="400"
              alt="Logo"
              className="mx-auto"
          />  
          <h1 className="text-3xl font-medium bg-gradient-to-r from-[#da0443] via-[#e8356a] to-[#ff75d8] inline-block text-transparent bg-clip-text text-gray-900 py-2">
            Start translating now!
          </h1>
        </div>

        {/* Main Interface */}  
        <div ref={settingsRef} className="max-w-2xl mx-auto space-y-8">
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
          {results.length > 0 && !isProcessing && <ResultsDisplay results={results} handleTranslate={handleTranslate}/>}
        </div>
      </main>
    </div>
  )
}
