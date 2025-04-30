import React from 'react';
import { Alert, Button, Space } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

/**
 * Banner component that prompts new users to configure their WhatsApp and CRM settings
 * @param {Object} props - Component props
 * @param {boolean} props.visible - Whether the banner should be visible
 * @param {Function} props.onClose - Function to call when the banner is closed
 */
const SetupBanner = ({ visible, onClose }) => {
  if (!visible) return null;

  return (
    <Alert
      message="Welcome to WAffy Dashboard!"
      description={
        <div>
          <p>To get started, please configure your WhatsApp and CRM settings to enable full functionality.</p>
          <Space>
            <Link to="/settings">
              <Button type="primary" icon={<SettingOutlined />}>
                Configure Settings
              </Button>
            </Link>
            <Button type="link" onClick={onClose}>
              Remind me later
            </Button>
          </Space>
        </div>
      }
      type="info"
      showIcon
      closable
      onClose={onClose}
      style={{ marginBottom: 24 }}
      banner
    />
  );
};

export default SetupBanner;
