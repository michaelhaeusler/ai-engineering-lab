/**
 * Header Component
 * Displays the app title and settings button
 */

import { MessageCircle, Settings } from 'lucide-react'

interface HeaderProps {
  onSettingsClick: () => void
}

export const Header = ({ onSettingsClick }: HeaderProps) => {
  return (
    <div className="border-b border-neutral-200 bg-white/80 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-neutral-600 to-neutral-800 rounded-xl flex items-center justify-center">
            <MessageCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-neutral-900">RAG Chat</h1>
            <p className="text-sm text-neutral-500">AI-powered document chat</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            data-testid="header-settings-button"
            onClick={onSettingsClick}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4 text-gray-500 hover:text-gray-700" />
          </button>
        </div>
      </div>
    </div>
  )
}
