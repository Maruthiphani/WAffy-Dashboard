/**
 * User service for handling user-related API calls
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Create a user in the database after Clerk signup
 * @param {Object} userData - User data from Clerk
 * @returns {Promise} - Promise with the created user data
 */
export const createUser = async (userData) => {
  try {
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

/**
 * Get error logs for a specific user, optionally filtered by error types
 * @param {string} userId - The user's clerk ID
 * @param {Array<string>} errorTypes - Optional array of error types to filter by (e.g., ['WhatsApp Error', 'HubSpot Error'])
 * @returns {Promise<Array>} - Promise with the error logs
 */
export const getUserErrorLogs = async (userId, errorTypes = []) => {
  try {
    let url = `${API_URL}/error-logs?clerk_id=${userId}`;
    
    // Add error types to the query if provided
    if (errorTypes && errorTypes.length > 0) {
      errorTypes.forEach(type => {
        url += `&error_types=${encodeURIComponent(type)}`;
      });
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching error logs:', error);
    return []; // Return empty array on error to prevent UI crashes
  }
};

/**
 * Get user data by Clerk ID
 * @param {string} clerkId - Clerk user ID
 * @returns {Promise} - Promise with the user data or null if not found
 */
export const getUserByClerkId = async (clerkId) => {
  try {
    const response = await fetch(`${API_URL}/users/${clerkId}`);

    if (!response.ok) {
      if (response.status === 404) {
        return null; // User not found
      }
      console.warn(`Error fetching user: ${response.status}`);
      return null; // Return null instead of throwing for any error
    }

    return await response.json();
  } catch (error) {
    console.error('Network error fetching user:', error);
    // Return null instead of throwing the error
    return null;
  }
};

/**
 * Update user settings
 * @param {string} clerkId - Clerk user ID
 * @param {Object} settingsData - User settings data
 * @returns {Promise} - Promise with the updated user data or error object
 */
export const updateUserSettings = async (clerkId, settingsData) => {
  try {
    const response = await fetch(`${API_URL}/users/${clerkId}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settingsData),
    });

    if (!response.ok) {
      console.warn(`Error updating user settings: ${response.status}`);
      return { error: `Failed to update settings (${response.status})` };
    }

    return await response.json();
  } catch (error) {
    console.error('Network error updating user settings:', error);
    return { error: 'Network error while updating settings' };
  }
};

/**
 * Get user settings
 * @param {string} clerkId - Clerk user ID
 * @returns {Promise} - Promise with the user settings data
 */
export const getUserSettings = async (clerkId) => {
  try {
    const response = await fetch(`${API_URL}/users/${clerkId}/settings`);

    if (!response.ok) {
      if (response.status === 404) {
        return null; // Settings not found
      }
      if (response.status === 500) {
        console.warn('Server error fetching settings, returning empty settings');
        // Return empty settings object instead of throwing an error
        return {
          message: 'Could not load settings due to a server error. Please save your settings again.'
        };
      }
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user settings:', error);
    // Return a user-friendly error message instead of throwing
    return {
      message: 'Could not load settings. Please try again or save your settings.'
    };
  }
};



/**
 * Get orders for the current user
 * @param {string} clerkId - Optional Clerk user ID to filter by
 * @returns {Promise} - Promise with the list of orders
 */
export const getOrders = async (clerkId = null) => {
  try {
    const url = clerkId ? `${API_URL}/orders?clerk_id=${clerkId}` : `${API_URL}/orders`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch orders');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching orders:', error);
    return [];
  }
};



/**
 * Get customers for the current user
 * @param {string} clerkId - Optional Clerk user ID to filter by
 * @returns {Promise} - Promise with the list of customers
 */
export const getCustomers = async (clerkId = null) => {
  try {
    const url = clerkId ? `${API_URL}/customers?clerk_id=${clerkId}` : `${API_URL}/customers`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching customers:', error);
    return [];
  }
};



/**
 * Get enquiries for the current user
 * @param {string} clerkId - Optional Clerk user ID to filter by
 * @returns {Promise} - Promise with the list of enquiries
 */
export const getEnquiries = async (clerkId = null) => {
  try {
    const url = clerkId ? `${API_URL}/enquiries?clerk_id=${clerkId}` : `${API_URL}/enquiries`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching enquiries:', error);
    return [];
  }
};



/**
 * Get all issues from the backend
 * @returns {Promise} - Promise with the list of issues
 */
/**
 * Get issues for the current user
 * @param {string} clerkId - Optional Clerk user ID to filter by
 * @returns {Promise} - Promise with the list of issues
 */
export const getIssues = async (clerkId) => {
  try {
    const url = clerkId ? `${API_URL}/issues?clerk_id=${clerkId}` : `${API_URL}/issues`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Error fetching issues: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching issues:', error);
    return [];
  }
};

export const getResponseMetrics = async (clerkId, days = 30) => {
  try {
    const url = clerkId 
      ? `${API_URL}/response-metrics?clerk_id=${clerkId}&days=${days}` 
      : `${API_URL}/response-metrics?days=${days}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Error fetching response metrics: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching response metrics:', error);
    return [];
  }
};

/**
 * Get WhatsApp access token from user settings
 * @param {string} clerkId - Clerk user ID
 * @returns {Promise} - Promise with the token or null if not found
 */
export const getWhatsAppToken = async (clerkId) => {
  try {
    // Get all user settings
    const settings = await getUserSettings(clerkId);
    
    // Check if settings exist and contain the token
    if (settings && settings.whatsapp_access_token) {
      return { token: settings.whatsapp_access_token };
    }
    
    // If no token found
    return { token: null, message: 'No WhatsApp token found in settings' };
  } catch (error) {
    console.error('Error fetching WhatsApp token:', error);
    return { token: null, error: 'Failed to retrieve WhatsApp token' };
  }
};

/**
 * Get WhatsApp verify token from user settings
 * @param {string} clerkId - Clerk user ID
 * @returns {Promise} - Promise with the verify token or null if not found
 */
export const getWhatsAppVerifyToken = async (clerkId) => {
  try {
    // Get all user settings
    const settings = await getUserSettings(clerkId);
    
    // Check if settings exist and contain the verify token
    if (settings && settings.whatsapp_verify_token) {
      return { verifyToken: settings.whatsapp_verify_token };
    }
    
    // If no verify token found
    return { verifyToken: null, message: 'No WhatsApp verify token found in settings' };
  } catch (error) {
    console.error('Error fetching WhatsApp verify token:', error);
    return { verifyToken: null, error: 'Failed to retrieve WhatsApp verify token' };
  }
};

//code to update order status in db 
export const updateOrderStatus = async (orderNumber, status) => {
  //const url = `${API_URL}/api/orders/${orderNumber}`;
  const url = `${API_URL}/orders/${orderNumber}`;

  console.log("PUT request to:", url); // Add this line

  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    if (!response.ok) throw new Error("Failed to update status");
    return await response.json();
  } catch (err) {
    console.error("Error updating order status:", err);
    throw err;
  }
};



