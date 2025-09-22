"use client"

import { useState, useEffect, useRef } from "react"
import { DEFAULT_SOURCE_LANGUAGE, DEFAULT_TARGET_LANGUAGE, API_URL } from "@/constants";
import { Header } from "@/components/header"
import { UploadSection } from "@/components/upload-section"
import { LanguageSelector } from "@/components/language-selector"
import { ProcessingStatus } from "@/components/processing-status"
import { ResultsDisplay } from "@/components/results-display"
import { Background } from "@/components/background"
import Image from "next/image"

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [sourceLanguage, setSourceLanguage] = useState(DEFAULT_SOURCE_LANGUAGE)
  const [targetLanguage, setTargetLanguage] = useState(DEFAULT_TARGET_LANGUAGE)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [results, setResults] = useState<any[]>([])

  const settingsRef = useRef<HTMLDivElement>(null)

  const handleFilesUpload = (files: File[]) => {
    setUploadedFiles(files)
    setResults([])
  }
  const pollForResult = async (jobId: string) => {
    const maxAttempts = 6
    const interval = 10000 // 10 seconds
    let attempt = 0

    return new Promise<any>((resolve, reject) => {
      const checkResult = async () => {
        try {
          const res = await fetch(`${API_URL}/result/${jobId}`)
          if (!res.ok) throw new Error("Failed to fetch result")
          const data = await res.json()

          if (data.status === "done") {
            resolve(data.result)
            return
          }

          attempt++
          if (attempt >= maxAttempts) {
            reject(new Error("Result not ready after multiple attempts"))
            return
          }

          setTimeout(checkResult, interval)
        } catch (err) {
          reject(err)
        }
      }

      checkResult()
    })
  }


  const handleTranslate = async () => {
    if (uploadedFiles.length === 0) return

    setIsProcessing(true)
    setProcessingProgress(0)

    try {
      const formData = new FormData()
      uploadedFiles.forEach((file) => formData.append("image", file))
      formData.append("source_lang", sourceLanguage)
      formData.append("target_lang", targetLanguage)

      const response = await fetch(`${API_URL}/process`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) throw new Error("Failed to start job")
      const { job_ids } = await response.json()
      console.log("Job IDs:", job_ids)

      const resultsData = await Promise.all(
        job_ids.map(async (jobId: string) => {
          const result = await pollForResult(jobId)
          return result 
        })
      )

      const resultsArray = resultsData.map((item: any, idx: number) => ({
        id: idx,
        originalFile: uploadedFiles[idx],
        originalUrl: URL.createObjectURL(uploadedFiles[idx]),
        translatedUrl: `data:image/png;base64,${item.image_bytes}`,
        detectedText: item.translated_data?.map((t: any) => t.text) || ["No text detected"],
        translatedText: item.translated_data?.map((t: any) => t.translated_text) || ["No text translated"],
      }))

      setProcessingProgress(100)
      setResults(resultsArray)
    } catch (error) {
      console.error("Error translating images:", error)
      setProcessingProgress(0)
    } finally {
      setIsProcessing(false)
    }
  }


  // useEffect(() => {
  //   // test api endpoint at 127.001:5000/api/hello
  //   const testApiEndpoint = async () => {
  //     try {
  //       const response = await fetch("http://127.0.0.1:5000/api/hello")
  //       if (!response.ok) {
  //         throw new Error("Network response was not ok")
  //       }
  //       const data = await response.json()
  //       console.log("API Test Response:", data)
  //     } catch (error) {
  //       console.error("Error testing API endpoint:", error)
  //     }
  //   }
  //   testApiEndpoint()
  // }, [])

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
