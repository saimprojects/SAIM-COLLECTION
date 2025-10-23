import React, { useRef, useState } from 'react'
import axios from 'axios'
import Editor from './components/Editor'

export default function App() {
  const fileRef = useRef(null)
  const [loading, setLoading] = useState(false)
  const [asset, setAsset] = useState(null) // { id, image_url, width, height, elements }

  const onUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    try {
      const form = new FormData()
      form.append('image', file)
      const { data } = await axios.post('/api/upload/', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setAsset(data)
    } catch (err) {
      console.error(err)
      alert('Upload failed. Check backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const onSave = async (updatedElements) => {
    if (!asset) return
    const { data } = await axios.put(`/api/images/${asset.id}/`, { elements: updatedElements })
    setAsset(data)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="p-4 border-b bg-white">
        <h1 className="text-xl font-semibold">AI Image Text Editor</h1>
      </header>

      <main className="flex-1 flex">
        <aside className="w-72 p-4 bg-white border-r">
          <div className="space-y-2">
            <button
              onClick={() => fileRef.current?.click()}
              className="w-full py-2 px-3 bg-blue-600 text-white rounded hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Upload Image'}
            </button>
            <input
              type="file"
              accept="image/*"
              ref={fileRef}
              className="hidden"
              onChange={onUpload}
            />

            {asset && (
              <div className="text-sm text-gray-600">
                <div>Image ID: {asset.id}</div>
                <div>Detected elements: {asset.elements?.length ?? 0}</div>
              </div>
            )}
            <p className="text-xs text-gray-500">
              Tip: Upload an AI-generated image with visible text. The backend will detect text, font size, and color.
            </p>
          </div>
        </aside>

        <section className="flex-1 overflow-auto">
          {!asset ? (
            <div className="h-full flex items-center justify-center text-gray-500">
              Upload an image to begin.
            </div>
          ) : (
            <Editor
              imageUrl={asset.image_url}
              originalSize={{ width: asset.width, height: asset.height }}
              initialElements={asset.elements}
              onSave={onSave}
            />
          )}
        </section>
      </main>
      <footer className="p-3 text-center text-xs text-gray-500 border-t bg-white">
        Backend: Django + Tesseract OCR · Frontend: React + Konva · Export or Save your edits
      </footer>
    </div>
  )
}