import React from 'react';

interface SettingsSidebarProps {
  showSettings: boolean;
  isLongFormMode: boolean;
  setIsLongFormMode: (value: boolean) => void;
  maxTokens: number;
  setMaxTokens: (value: number) => void;
}

const SettingsSidebar: React.FC<SettingsSidebarProps> = ({
  showSettings,
  isLongFormMode,
  setIsLongFormMode,
  maxTokens,
  setMaxTokens,
}) => {
  return (
    <aside className={`w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-4 overflow-y-auto shrink-0 transition-transform duration-300 ease-in-out ${showSettings ? 'translate-x-0' : 'translate-x-full absolute right-0 h-full'}`}>
      <h3 className="text-lg font-semibold mb-4">설정</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <label htmlFor="long-form-mode" className="text-sm font-medium">긴 소설 모드</label>
          <input
            type="checkbox"
            id="long-form-mode"
            checked={isLongFormMode}
            onChange={(e) => setIsLongFormMode(e.target.checked)}
            className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500"
          />
        </div>
        <div>
          <label htmlFor="max-tokens" className="block text-sm font-medium mb-1">최대 토큰: {maxTokens}</label>
          <input
            type="range"
            id="max-tokens"
            min="500"
            max="8000"
            step="100"
            value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
        </div>
      </div>
    </aside>
  );
};

export default SettingsSidebar; 