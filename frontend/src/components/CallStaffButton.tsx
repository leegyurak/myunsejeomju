import React from 'react';

interface CallStaffButtonProps {
  onCallStaff: () => void;
}

const CallStaffButton: React.FC<CallStaffButtonProps> = ({ onCallStaff }) => {
  return (
    <button className="call-staff-button" onClick={onCallStaff}>
      <span>직원<br/>호출</span>
    </button>
  );
};

export default CallStaffButton;