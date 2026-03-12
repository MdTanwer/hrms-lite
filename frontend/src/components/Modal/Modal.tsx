import type { MouseEvent, ReactNode } from 'react';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: ModalSize;
  showCloseButton?: boolean;
}

const MODAL_SIZE_CLASSES: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  '2xl': 'max-w-6xl',
};

const DEFAULT_MODAL_SIZE: ModalSize = 'md';

function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = DEFAULT_MODAL_SIZE,
  showCloseButton = true,
}: ModalProps): React.ReactElement {
  const handleBackdropClick = (e: MouseEvent<HTMLDivElement>): void => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className={`fixed inset-0 bg-black bg-opacity-90 backdrop-blur-sm flex items-center justify-center z-[999999] p-4 transition-all duration-300 ${
        isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
      }`}
      onClick={handleBackdropClick}
    >
      <div 
        className={`flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-h-[calc(100vh-2rem)] ${MODAL_SIZE_CLASSES[size]} transform transition-all duration-300 ${
          isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <div className="flex items-center justify-between flex-shrink-0 p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
          {showCloseButton && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
            >
              <svg 
                className="w-6 h-6" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M6 18L18 6M6 6l12 12" 
                />
              </svg>
            </button>
          )}
        </div>
        
        <div className="p-6 overflow-y-auto min-h-0 flex-1">
          {children}
        </div>
      </div>
    </div>
  );
}

export default Modal;
