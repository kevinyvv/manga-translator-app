import { Zap, Eye, Globe, Download } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function FeatureCards() {
  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "AI-powered text detection and translation in seconds",
    },
    {
      icon: Eye,
      title: "Layout Preservation",
      description: "Maintains original manga layout and visual style",
    },
    {
      icon: Globe,
      title: "Multiple Languages",
      description: "Support for 50+ languages with high accuracy",
    },
    {
      icon: Download,
      title: "Easy Export",
      description: "Download translated pages in high quality",
    },
  ]

  return (
    <div className="mt-16">
      <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">Why Choose MangaTranslate?</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <Card key={index} className="text-center">
            <CardContent className="p-6">
              <feature.icon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
