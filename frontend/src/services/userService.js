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
 * Get user data by Clerk ID
 * @param {string} clerkId - Clerk user ID
 * @returns {Promise} - Promise with the user data
 */
export const getUserByClerkId = async (clerkId) => {
  try {
    const response = await fetch(`${API_URL}/users/${clerkId}`);

    if (!response.ok) {
      if (response.status === 404) {
        return null; // User not found
      }
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
};

/**
 * Update user settings
 * @param {string} clerkId - Clerk user ID
 * @param {Object} settingsData - User settings data
 * @returns {Promise} - Promise with the updated user data
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
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating user settings:', error);
    throw error;
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
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user settings:', error);
    throw error;
  }
};
