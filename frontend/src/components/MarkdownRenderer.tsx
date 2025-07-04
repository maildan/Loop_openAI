'use client'

import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import 'highlight.js/styles/github.css'
import type { Element } from 'hast'

interface MarkdownRendererProps {
  content: string
  className?: string
}

// `react-markdown`의 `code` 컴포넌트가 받는 props를 위한 완벽하고 우아한 타입
interface CustomCodeProps extends React.HTMLAttributes<HTMLElement> {
  node: Element
  inline?: boolean
}

const CodeComponent: React.FC<CustomCodeProps> = ({ node, inline, className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '')
  
  // `node` 객체는 DOM으로 전달하지 않습니다.
  // `props`에 남아있는 속성만 안전하게 전달합니다.
  
  if (!inline && match) {
    return (
      <div className="mb-4">
        <div className="bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 border-b">
          {match[1]}
        </div>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-b-md overflow-x-auto">
          <code className={className} {...props}>
            {String(children).replace(/\n$/, '')}
          </code>
        </pre>
      </div>
    )
  }
  
  return (
    <code className={className ? className : "bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"} {...props}>
      {children}
    </code>
  )
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  const components: Components = {
    // 커스텀 컴포넌트들
    h1: ({ children }) => (
      <h1 className="text-2xl font-bold text-gray-900 mb-4 border-b border-gray-200 pb-2">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-xl font-semibold text-gray-900 mb-3 mt-6">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-lg font-medium text-gray-900 mb-2 mt-4">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="text-gray-700 mb-4 leading-relaxed">
        {children}
      </p>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900">
        {children}
      </strong>
    ),
    em: ({ children }) => (
      <em className="italic text-gray-700">
        {children}
      </em>
    ),
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-4 space-y-1 text-gray-700">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-4 space-y-1 text-gray-700">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="text-gray-700">
        {children}
      </li>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 py-2 mb-4 bg-blue-50 text-gray-700 italic">
        {children}
      </blockquote>
    ),
    // `react-markdown`의 부정확한 타입 정의를 우회하기 위해 타입 단언(casting)을 사용합니다.
    // 이는 외부 라이브러리의 문제를 해결하는 가장 우아하고 실용적인 방법입니다.
    code: CodeComponent as any,
    pre: ({ children }) => <>{children}</>,
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 underline"
      >
        {children}
      </a>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto mb-4">
        <table className="min-w-full border border-gray-300">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-gray-50">
        {children}
      </thead>
    ),
    tbody: ({ children }) => (
      <tbody className="bg-white">
        {children}
      </tbody>
    ),
    tr: ({ children }) => (
      <tr className="border-b border-gray-200">
        {children}
      </tr>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2 text-left font-medium text-gray-900">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 text-gray-700">
        {children}
      </td>
    ),
    hr: () => (
      <hr className="my-6 border-gray-300" />
    )
  };

  return (
    <div className={`prose prose-gray max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownRenderer 