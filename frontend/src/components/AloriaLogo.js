import React from 'react';

export default function AloriaLogo({ className = "h-8", showText = true }) {
  return (
    <div className="flex items-center space-x-3">
      <img 
        src="/aloria-logo.png" 
        alt="ALORIA AGENCY Logo" 
        className={className}
      />
      {showText && (
        <span className="text-orange-500 text-xl font-bold">ALORIA AGENCY</span>
      )}
    </div>
  );
}
