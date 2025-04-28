/**
 * Business service for handling business-related API calls
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Get all business types
 * @returns {Promise} - Promise with the business types data
 */
export const getBusinessTypes = async () => {
  try {
    const response = await fetch(`${API_URL}/business/types`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching business types:', error);
    throw error;
  }
};

/**
 * Add a new business type
 * @param {string} typeName - The name of the new business type
 * @returns {Promise} - Promise with the created business type data
 */
export const addBusinessType = async (typeName) => {
  try {
    const response = await fetch(`${API_URL}/business/types`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: typeName }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error adding business type:', error);
    throw error;
  }
};

/**
 * Get all business tags
 * @returns {Promise} - Promise with the business tags data
 */
export const getBusinessTags = async () => {
  try {
    const response = await fetch(`${API_URL}/business/tags`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching business tags:', error);
    throw error;
  }
};

/**
 * Get business tags for a specific business type
 * @param {number} businessTypeId - The business type ID
 * @returns {Promise} - Promise with the business tags data for the specified business type
 */
export const getBusinessTagsByType = async (businessTypeId) => {
  if (!businessTypeId) return [];
  
  try {
    const response = await fetch(`${API_URL}/business/types/${businessTypeId}/tags`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching business tags by type:', error);
    throw error;
  }
};

/**
 * Add a new business tag
 * @param {string} tagName - The name of the new business tag
 * @param {number} businessTypeId - The business type ID
 * @returns {Promise} - Promise with the created business tag data
 */
export const addBusinessTag = async (tagName, businessTypeId) => {
  try {
    const response = await fetch(`${API_URL}/business/tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        name: tagName,
        business_type_id: businessTypeId 
      }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error adding business tag:', error);
    throw error;
  }
};

/**
 * Get business tags for a specific user
 * @param {string} userId - The user ID
 * @returns {Promise} - Promise with the user's business tags or empty array if error
 */
export const getUserBusinessTags = async (userId) => {
  try {
    const response = await fetch(`${API_URL}/users/${userId}/business-tags`);

    if (!response.ok) {
      console.warn(`Error fetching user business tags: ${response.status}`);
      return []; // Return empty array instead of throwing
    }

    return await response.json();
  } catch (error) {
    console.error('Network error fetching user business tags:', error);
    return []; // Return empty array on network error
  }
};

/**
 * Update user's business tags
 * @param {string} userId - The user ID
 * @param {Array} tagIds - Array of tag IDs
 * @returns {Promise} - Promise with the updated user business tags or error object
 */
export const updateUserBusinessTags = async (userId, tagIds) => {
  try {
    const response = await fetch(`${API_URL}/users/${userId}/business-tags`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tagIds }),
    });

    if (!response.ok) {
      console.warn(`Error updating user business tags: ${response.status}`);
      return { error: `Failed to update business tags (${response.status})` };
    }

    return await response.json();
  } catch (error) {
    console.error('Network error updating user business tags:', error);
    return { error: 'Network error while updating business tags' };
  }
};
