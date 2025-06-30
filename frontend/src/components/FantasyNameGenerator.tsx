'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '@/components/ui/Card'
import { Sparkles, RefreshCw, Copy, CheckCircle } from 'lucide-react'
import { baseUrl } from '@/lib/utils'

interface FantasyNameGeneratorProps {
  className?: string
}

const FantasyNameGenerator: React.FC<FantasyNameGeneratorProps> = ({ className }) => {
  const [race, setRace] = useState<string>('elf')
  const [gender, setGender] = useState<string>('male')
  const [count, setCount] = useState<number>(5)
  const [names, setNames] = useState<string[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [copied, setCopied] = useState<string | null>(null)

  const races = ['elf', 'dwarf', 'human', 'orc', 'halfling', 'dragon', 'fairy', 'goblin', 'demon', 'angel']
  const genders = ['male', 'female', 'neutral']

  const generateNames = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${baseUrl}/api/fantasy-names?race=${race}&gender=${gender}&count=${count}`)
      
      if (!response.ok) {
        throw new Error('서버 오류가 발생했습니다.')
      }
      
      const data = await response.json()
      setNames(data.names || [])
    } catch (error) {
      console.error('이름 생성 오류:', error)
      setNames(['서버 연결에 실패했습니다. 다시 시도해주세요.'])
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (name: string) => {
    navigator.clipboard.writeText(name)
    setCopied(name)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <Card 
      variant="elevated" 
      className={className}
      bordered
      hoverable
    >
      <CardHeader>
        <CardTitle className="flex items-center">
          <Sparkles className="w-5 h-5 mr-2 text-amber-500" />
          판타지 이름 생성기
        </CardTitle>
        <CardDescription>
          다양한 종족과 성별에 맞는 판타지 이름을 생성해보세요
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                종족
              </label>
              <select
                value={race}
                onChange={(e) => setRace(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                {races.map((r) => (
                  <option key={r} value={r}>
                    {r.charAt(0).toUpperCase() + r.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                성별
              </label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                {genders.map((g) => (
                  <option key={g} value={g}>
                    {g === 'male' ? '남성' : g === 'female' ? '여성' : '중성'}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex justify-between">
              <span>생성할 이름 수</span>
              <span className="text-blue-600 dark:text-blue-400">{count}</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600 dark:accent-blue-500"
            />
          </div>
          
          <Button
            variant="default"
            size="default"
            disabled={loading}
            onClick={generateNames}
            className="w-full"
          >
            {loading && <RefreshCw className="w-4 h-4 mr-2 animate-spin" />}
            이름 생성하기
          </Button>
        </div>
        
        {names.length > 0 && (
          <div className="mt-6 space-y-2">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              생성된 이름
            </h3>
            <div className="space-y-2">
              {names.map((name, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800/50 rounded-md border border-gray-200 dark:border-gray-700"
                >
                  <span className="font-medium">{name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(name)}
                    className="rounded-full"
                  >
                    {copied === name ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FantasyNameGenerator 
