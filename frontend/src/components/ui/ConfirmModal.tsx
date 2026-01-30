import React from 'react';
import Modal from '../Modal/Modal';
import Button from './Button';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
  icon?: React.ReactNode;
  customContent?: React.ReactNode;
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  isLoading = false,
  icon,
  customContent
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'danger':
        return {
          iconColor: 'text-red-600 dark:text-red-400',
          buttonClass: 'bg-red-600 hover:bg-red-700 focus:ring-red-500 dark:bg-red-600 dark:hover:bg-red-700',
          defaultIcon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.932-3L13.932 4c-.77-1.333-2.694-2-3.462-2H6.53c-.77 0-1.692.667-1.932 2L3.068 15c.77 1.333 2.692 2 3.462 2h13.856c.77 0 1.692-.667 1.932-2l1.07-4.586" />
            </svg>
          )
        };
      case 'warning':
        return {
          iconColor: 'text-yellow-600 dark:text-yellow-400',
          buttonClass: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500 dark:bg-yellow-600 dark:hover:bg-yellow-700',
          defaultIcon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.932-3L13.932 4c-.77-1.333-2.694-2-3.462-2H6.53c-.77 0-1.692.667-1.932 2L3.068 15c.77 1.333 2.692 2 3.462 2h13.856c.77 0 1.692-.667 1.932-2l1.07-4.586" />
            </svg>
          )
        };
      case 'info':
        return {
          iconColor: 'text-blue-600 dark:text-blue-400',
          buttonClass: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 dark:bg-blue-600 dark:hover:bg-blue-700',
          defaultIcon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
    >
      <div className="space-y-4">
        {/* Icon and message section */}
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className={styles.iconColor}>
              {icon || styles.defaultIcon}
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 break-words">
              {title}
            </h3>
            <div className="mt-1 text-sm text-gray-500 dark:text-gray-400 break-words">
              {message}
            </div>
          </div>
        </div>

        {/* Custom content section */}
        {customContent && (
          <div className="mt-4">
            {customContent}
          </div>
        )}
      </div>
      
      {/* Action buttons */}
      <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-600">
        <Button
          variant="outline"
          onClick={onClose}
          disabled={isLoading}
          className="flex-1 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          {cancelText}
        </Button>
        <Button
          variant="destructive"
          onClick={onConfirm}
          disabled={isLoading}
          className="flex-1"
        >
          {isLoading ? 'Loading...' : confirmText}
        </Button>
      </div>
    </Modal>
  );
};

export default ConfirmModal;
