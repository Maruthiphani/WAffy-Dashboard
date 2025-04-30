import React, { useState, useEffect } from 'react';
import { Alert, Button, Space, Typography, Collapse } from 'antd';
import { WarningOutlined, SettingOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { getUserErrorLogs } from '../services/userService';

const { Text } = Typography;
const { Panel } = Collapse;

/**
 * Banner component that displays WhatsApp and HubSpot errors to users
 * @param {Object} props - Component props
 * @param {string} props.userId - The user's ID
 */
const ErrorBanner = ({ userId }) => {
  const [errors, setErrors] = useState([]);
  const [visible, setVisible] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      fetchErrors();
    }
  }, [userId]);

  const fetchErrors = async () => {
    try {
      setLoading(true);
      // Fetch only WhatsApp and HubSpot errors
      const errorLogs = await getUserErrorLogs(userId, ['WhatsApp Error', 'HubSpot Error']);
      
      // Check if we have valid error logs
      if (Array.isArray(errorLogs)) {
        setErrors(errorLogs);
      } else {
        console.warn('Received non-array response from error logs API:', errorLogs);
        setErrors([]);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching error logs:', error);
      setErrors([]);
      setLoading(false);
    }
  };

  const handleClose = () => {
    setVisible(false);
  };

  // Group errors by type
  const whatsAppErrors = errors.filter(error => error.error_type === 'WhatsApp Error');
  const hubspotErrors = errors.filter(error => error.error_type === 'HubSpot Error');

  // Don't show the banner while loading or if there are no errors or if it's been dismissed
  if (!visible || loading || errors.length === 0) {
    return null;
  }

  const getErrorMessage = (error) => {
    // Extract the most relevant part of the error message
    let message = error.error_message;
    
    // For WhatsApp errors, often the error message contains JSON
    if (error.error_type === 'WhatsApp Error' && message.includes('{')) {
      try {
        // Try to parse JSON in the error message
        const jsonStart = message.indexOf('{');
        const jsonPart = message.substring(jsonStart);
        const errorData = JSON.parse(jsonPart);
        
        // Extract the most useful information
        if (errorData.error && errorData.error.message) {
          return errorData.error.message;
        }
      } catch (e) {
        // If parsing fails, just return the original message
      }
    }
    
    return message;
  };

  const getErrorAction = (errorType) => {
    if (errorType === 'WhatsApp Error') {
      return (
        <Link to="/settings">
          <Button type="primary" size="small" icon={<SettingOutlined />}>
            Fix WhatsApp Settings
          </Button>
        </Link>
      );
    } else if (errorType === 'HubSpot Error') {
      return (
        <Link to="/settings">
          <Button type="primary" size="small" icon={<SettingOutlined />}>
            Fix HubSpot Settings
          </Button>
        </Link>
      );
    }
    return null;
  };

  return (
    <Alert
      message={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <WarningOutlined style={{ color: '#ff4d4f' }} />
            <Text strong>Configuration Errors Detected</Text>
          </Space>
          <Button 
            type="text" 
            icon={<CloseCircleOutlined />} 
            onClick={handleClose}
            size="small"
          />
        </div>
      }
      description={
        <div>
          {whatsAppErrors.length > 0 && (
            <Collapse ghost>
              <Panel 
                header={<Text type="danger">{`WhatsApp Configuration Issues (${whatsAppErrors.length})`}</Text>} 
                key="whatsapp"
              >
                {whatsAppErrors.map((error, index) => (
                  <div key={`whatsapp-${index}`} style={{ marginBottom: 8 }}>
                    <Text type="secondary">{new Date(error.created_at).toLocaleString()}</Text>
                    <br />
                    <Text>{getErrorMessage(error)}</Text>
                  </div>
                ))}
                {getErrorAction('WhatsApp Error')}
              </Panel>
            </Collapse>
          )}
          
          {hubspotErrors.length > 0 && (
            <Collapse ghost>
              <Panel 
                header={<Text type="danger">{`HubSpot Configuration Issues (${hubspotErrors.length})`}</Text>} 
                key="hubspot"
              >
                {hubspotErrors.map((error, index) => (
                  <div key={`hubspot-${index}`} style={{ marginBottom: 8 }}>
                    <Text type="secondary">{new Date(error.created_at).toLocaleString()}</Text>
                    <br />
                    <Text>{getErrorMessage(error)}</Text>
                  </div>
                ))}
                {getErrorAction('HubSpot Error')}
              </Panel>
            </Collapse>
          )}
        </div>
      }
      type="error"
      style={{ marginBottom: 24 }}
      banner
    />
  );
};

export default ErrorBanner;
