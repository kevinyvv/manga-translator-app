import { Loader2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface ProcessingStatusProps {
  progress: number
}

export function ProcessingStatus({ progress }: ProcessingStatusProps) {
  const getStatusText = () => {
    if (progress < 30) return "Analyzing images..."
    if (progress < 60) return "Detecting text regions..."
    if (progress < 90) return "Translating text..."
    return "Finalizing results..."
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Loader2 className="h-5 w-5 animate-spin text-[#da0443]" />
          <h3 className="text-lg font-semibold text-gray-900">Processing Your Manga</h3>
        </div>

        <div className="space-y-3">
          <Progress value={progress} className="w-full" />
          <div className="flex justify-between text-sm text-gray-600">
            <span>{getStatusText()}</span>
            <span>{progress}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
