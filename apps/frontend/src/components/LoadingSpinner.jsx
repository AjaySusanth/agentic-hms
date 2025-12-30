import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Processing...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
