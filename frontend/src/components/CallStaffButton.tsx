import React from 'react';

interface CallStaffButtonProps {
  onCallStaff: () => void;
}

const CallStaffButton: React.FC<CallStaffButtonProps> = ({ onCallStaff }) => {
  return (
    <button className="call-staff-button" onClick={onCallStaff}>
      직원호출
    </button>
  );
};

export default CallStaffButton;