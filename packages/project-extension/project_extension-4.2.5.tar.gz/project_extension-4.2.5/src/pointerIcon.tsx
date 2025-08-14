import React from 'react';
export const PointerIcon: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%'
      }}
    >
      <div
        style={{
          backgroundColor: 'black',
          width: '10px',
          height: '10px',
          borderRadius: '50%'
        }}
      ></div>
    </div>
  );
};
