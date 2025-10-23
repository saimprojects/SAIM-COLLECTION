import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Stage, Layer, Image as KonvaImage, Text as KonvaText, Transformer } from 'react-konva'
import useImage from 'use-image'
import axios from 'axios'

function EditableText({ shapeProps, isSelected, onSelect, onChange }) {
  const shapeRef = useRef(null)
  const trRef = useRef(null)

  useEffect(() => {
    if (isSelected && trRef.current && shapeRef.current) {
      trRef.current.nodes([shapeRef.current])
      trRef.current.getLayer().batchDraw()
    }
  }, [isSelected])

  return (
    <>
      <KonvaText
        onClick={onSelect}
        onTap={onSelect}
        ref={shapeRef}
        {...shapeProps}
        draggable
        onDragEnd={(e) => {
          onChange({
            ...shapeProps,
            x: e.target.x(),
            y: e.target.y(),
          })
        }}
        onTransformEnd={(e) => {
          const node = shapeRef.current
          const scaleX = node.scaleX()
          const scaleY = node.scaleY()
          node.scaleX(1)
          node.scaleY(1)

          onChange({
            ...shapeProps,
            x: node.x(),
            y: node.y(),
            width: Math.max(5, node.width() * scaleX),
            height: Math.max(node.height() * scaleY),
            fontSize: Math.max(8, shapeProps.fontSize * scaleY),
          })
        }}
      />
      {isSelected && (
        <Transformer
          ref={trRef}
          rotateEnabled={false}
          enabledAnchors={['middle-left', 'middle-right', 'top-center', 'bottom-center']}
        />
      )}
    </>
  )
}

export default function Editor({ imageUrl, originalSize, initialElements, onSave }) {
  const [image] = useImage(imageUrl, 'anonymous')
  const [elements, setElements] = useState(initialElements || [])
  const [selectedId, setSelectedId] = useState(null)

  useEffect(() => {
    setElements(initialElements || [])
  }, [initialElements])

  const containerRef = useRef(null)
  const [stageSize, setStageSize] = useState({ width: 1000, height: 700 })
  useEffect(() => {
    const resize = () => {
      const w = window.innerWidth - 300
      const h = window.innerHeight - 120
      setStageSize({ width: Math.max(400, w), height: Math.max(300, h) })
    }
    resize()
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  const scale = useMemo(() => {
    const sw = stageSize.width / originalSize.width
    const sh = stageSize.height / originalSize.height
    return Math.min(sw, sh)
  }, [stageSize, originalSize])

  const handleDeselect = (e) => {
    const clickedOnEmpty = e.target === e.target.getStage()
    if (clickedOnEmpty) setSelectedId(null)
  }

  const updateElement = (id, newProps) => {
    setElements(prev => prev.map(el => (el.id === id ? { ...el, ...newProps } : el)))
  }

  const exportImage = () => {
    const uri = stageRef.current.toDataURL({ pixelRatio: 2 })
    const a = document.createElement('a')
    a.href = uri
    a.download = 'edited-image.png'
    a.click()
  }

  const stageRef = useRef(null)

  return (
    <div className="h-full w-full flex">
      <div className="flex-1 flex items-center justify-center">
        <div className="shadow bg-white m-4">
          <Stage
            ref={stageRef}
            width={originalSize.width * scale}
            height={originalSize.height * scale}
            onMouseDown={handleDeselect}
            onTouchStart={handleDeselect}
            className="bg-gray-100"
          >
            <Layer>
              {image && (
                <KonvaImage
                  image={image}
                  width={originalSize.width * scale}
                  height={originalSize.height * scale}
                />
              )}
              {elements.map(el => (
                <EditableText
                  key={el.id}
                  shapeProps={{
                    x: el.x * scale,
                    y: el.y * scale,
                    width: el.width * scale,
                    height: el.height * scale,
                    text: el.text,
                    fontFamily: el.fontFamily,
                    fontSize: el.fontSize * scale,
                    fill: el.fill,
                  }}
                  isSelected={el.id === selectedId}
                  onSelect={() => setSelectedId(el.id)}
                  onChange={(newProps) => {
                    const normalized = {
                      ...newProps,
                      x: newProps.x / scale,
                      y: newProps.y / scale,
                      width: newProps.width / scale,
                      height: newProps.height / scale,
                      fontSize: newProps.fontSize / scale,
                    }
                    updateElement(el.id, normalized)
                  }}
                />
              ))}
            </Layer>
          </Stage>
        </div>
      </div>

      <div className="w-80 p-4 bg-white border-l space-y-3">
        <div className="flex gap-2">
          <button
            className="flex-1 py-2 px-3 bg-emerald-600 text-white rounded hover:bg-emerald-700"
            onClick={() => onSave(elements)}
          >
            Save
          </button>
          <button
            className="flex-1 py-2 px-3 bg-slate-700 text-white rounded hover:bg-slate-800"
            onClick={exportImage}
          >
            Download PNG
          </button>
        </div>

        {selectedId ? (
          <Inspector
            element={elements.find(e => e.id === selectedId)}
            onChange={(patch) => updateElement(selectedId, patch)}
          />
        ) : (
          <div className="text-sm text-gray-500">Select a text layer to edit properties.</div>
        )}
      </div>
    </div>
  )
}

function Inspector({ element, onChange }) {
  if (!element) return null
  return (
    <div className="space-y-3">
      <div>
        <label className="block text-xs text-gray-600 mb-1">Text</label>
        <textarea
          className="w-full border rounded p-2 text-sm"
          value={element.text}
          onChange={(e) => onChange({ text: e.target.value })}
          rows={4}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-600 mb-1">Font Family</label>
          <select
            className="w-full border rounded p-2 text-sm"
            value={element.fontFamily}
            onChange={(e) => onChange({ fontFamily: e.target.value })}
          >
            <option>Arial</option>
            <option>Times New Roman</option>
            <option>Helvetica</option>
            <option>Georgia</option>
            <option>Courier New</option>
            <option>Inter</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1">Font Size</label>
          <input
            type="number"
            min="8"
            className="w-full border rounded p-2 text-sm"
            value={Math.round(element.fontSize)}
            onChange={(e) => onChange({ fontSize: Number(e.target.value) })}
          />
        </div>
      </div>

      <div>
        <label className="block text-xs text-gray-600 mb-1">Color</label>
        <input
          type="color"
          className="w-full h-10 border rounded"
          value={element.fill}
          onChange={(e) => onChange({ fill: e.target.value })}
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-600 mb-1">X</label>
          <input
            type="number"
            className="w-full border rounded p-2 text-sm"
            value={Math.round(element.x)}
            onChange={(e) => onChange({ x: Number(e.target.value) })}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1">Y</label>
          <input
            type="number"
            className="w-full border rounded p-2 text-sm"
            value={Math.round(element.y)}
            onChange={(e) => onChange({ y: Number(e.target.value) })}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-600 mb-1">Width</label>
          <input
            type="number"
            className="w-full border rounded p-2 text-sm"
            value={Math.round(element.width)}
            onChange={(e) => onChange({ width: Number(e.target.value) })}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1">Height</label>
          <input
            type="number"
            className="w-full border rounded p-2 text-sm"
            value={Math.round(element.height)}
            onChange={(e) => onChange({ height: Number(e.target.value) })}
          />
        </div>
      </div>
    </div>
  )
}