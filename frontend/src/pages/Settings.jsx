import React, { useState, useEffect } from "react";
import { useUser, SignedIn } from "@clerk/clerk-react";
import { updateUserSettings, getUserByClerkId, getUserSettings } from "../services/userService";
import { getBusinessTypes, addBusinessType, getBusinessTags, getBusinessTagsByType, addBusinessTag, getUserBusinessTags, updateUserBusinessTags } from "../services/businessService";
import DashboardHeader from "../components/DashboardHeader";

// Predefined category options
const CATEGORY_OPTIONS = [
  "new_order", "order_status", "general_inquiry", "complaint",
  "return_refund", "follow_up", "feedback", "others"
];

// Convert snake_case to Title Case
const formatName = (name) => {
  if (!name) return '';
  return name.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const Settings = () => {
  const { user, isLoaded } = useUser();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [userEmail, setUserEmail] = useState("");
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(null);
  const [customCategory, setCustomCategory] = useState("");
  
  // Business types and tags state
  const [businessTypes, setBusinessTypes] = useState([]);
  const [businessTags, setBusinessTags] = useState([]);
  const [businessTypeSpecificTags, setBusinessTypeSpecificTags] = useState([]);
  const [userBusinessTags, setUserBusinessTags] = useState([]);
  const [newBusinessType, setNewBusinessType] = useState("");
  const [newBusinessTag, setNewBusinessTag] = useState("");
  const [loadingBusinessType, setLoadingBusinessType] = useState(false);
  const [loadingBusinessTag, setLoadingBusinessTag] = useState(false);
  const [showAddBusinessType, setShowAddBusinessType] = useState(false);
  
  // Initialize form state with default values
  const defaultFormData = {
    firstName: '',
    lastName: '',
    businessName: '',
    businessDescription: '',
    contactPhone: '',
    contactEmail: '',
    businessWebsite: '',
    businessAddress: '',
    foundedYear: '',
    businessType: '',
    businessTags: [],
    categories: [], 
    whatsappPhoneNumberId: '',
    whatsappBusinessAccountId: '',
    whatsappVerifyToken: '',
    whatsappApiKey: '',
    whatsappAppId: '',
    whatsappAppSecret: '',
    hubspotAccessToken: '',
    hubspotSelectedCategories: [],
    useHubspot: false,
    useExcel: false,
    crmType: 'hubspot',
    otherCrmDetails: '',
    viewConsolidatedData: false
  };
  
  // Form state
  const [formData, setFormData] = useState(defaultFormData);

  // Fetch business types and tags
  useEffect(() => {
    const fetchBusinessData = async () => {
      try {
        const [typesData, tagsData] = await Promise.all([
          getBusinessTypes(),
          getBusinessTags()
        ]);
        
        setBusinessTypes(typesData);
        setBusinessTags(tagsData);
      } catch (error) {
        console.error('Error fetching business data:', error);
      }
    };
    
    fetchBusinessData();
  }, []);
  
  // Fetch business tags specific to the selected business type
  useEffect(() => {
    const fetchBusinessTagsByType = async () => {
      if (!formData.businessType) {
        setBusinessTypeSpecificTags([]);
        return;
      }
      
      try {
        const tagsData = await getBusinessTagsByType(formData.businessType);
        setBusinessTypeSpecificTags(tagsData);
      } catch (error) {
        console.error('Error fetching business tags by type:', error);
      }
    };
    
    fetchBusinessTagsByType();
  }, [formData.businessType]);
  
  // Load user settings if available
  useEffect(() => {
    if (isLoaded && user) {
      // Fetch user data and settings from our database
      const fetchUserData = async () => {
        try {
          if (!user) return;
          
          // Always set the email from Clerk first as a fallback
          setUserEmail(user.primaryEmailAddress?.emailAddress || "");
          
          // First get user data for email
          const dbUser = await getUserByClerkId(user.id);
          if (dbUser && dbUser.email) {
            setUserEmail(dbUser.email);
          }
          
          // Then get user settings and business tags
          // Use Promise.allSettled instead of Promise.all to handle partial failures
          const [userSettingsResult, userTagsResult] = await Promise.allSettled([
            getUserSettings(user.id),
            getUserBusinessTags(user.id)
          ]);
          
          // Process user settings if available
          if (userSettingsResult.status === 'fulfilled' && userSettingsResult.value) {
            const userSettings = userSettingsResult.value;
            
            // Process user business tags if available
            if (userTagsResult.status === 'fulfilled' && userTagsResult.value) {
              setUserBusinessTags(userTagsResult.value || []);
            }
            
            // Create a new form data object with safe defaults
            const newFormData = {
              ...defaultFormData,
              firstName: userSettings.first_name || "",
              lastName: userSettings.last_name || "",
              businessName: userSettings.business_name || "",
              businessDescription: userSettings.business_description || "",
              contactPhone: userSettings.contact_phone || "",
              contactEmail: userSettings.contact_email || "",
              businessWebsite: userSettings.business_website || "",
              businessAddress: userSettings.business_address || "",
              foundedYear: userSettings.founded_year || "",
              businessType: userSettings.business_type || "",
              businessTags: Array.isArray(userSettings.business_tags) ? userSettings.business_tags : [],
              categories: Array.isArray(userSettings.categories) ? userSettings.categories : [],
              whatsappPhoneNumberId: userSettings.whatsapp_phone_number_id || "",
              whatsappBusinessAccountId: userSettings.whatsapp_business_account_id || "",
              whatsappVerifyToken: userSettings.whatsapp_verify_token || "",
              whatsappApiKey: userSettings.whatsapp_api_key || "",
              whatsappAppId: userSettings.whatsapp_app_id || "",
              whatsappAppSecret: userSettings.whatsapp_app_secret || "",
              hubspotAccessToken: userSettings.hubspot_access_token || "",
              hubspotSelectedCategories: Array.isArray(userSettings.hubspot_selected_categories) ? 
                userSettings.hubspot_selected_categories : [],
              useHubspot: Boolean(userSettings.use_hubspot),
              useExcel: Boolean(userSettings.use_excel),
              crmType: userSettings.crm_type || "hubspot",
              otherCrmDetails: userSettings.other_crm_details || "",
              viewConsolidatedData: Boolean(userSettings.view_consolidated_data)
            };
            
            // Update form data with the new safe object
            setFormData(newFormData);
            console.log("Loaded settings from database");
          } else {
            // Fallback to Clerk data if no settings found
            setFormData({
              ...defaultFormData,
              firstName: user.firstName || "",
              lastName: user.lastName || "",
              categories: [""]
            });
            
            console.log("Using default settings");
          }
        } catch (error) {
          console.error("Error fetching user data:", error);
          // Fallback to Clerk email and default settings
          setUserEmail(user.primaryEmailAddress?.emailAddress || "");
          setFormData({
            ...defaultFormData,
            firstName: user.firstName || "",
            lastName: user.lastName || "",
            categories: [""]
          });
        }
      };
      
      fetchUserData();
    }
  }, [isLoaded, user]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };
  
  // Handle category input changes
  const handleCategoryChange = (index, value) => {
    try {
      // Create a safe copy of the current categories
      const currentCategories = Array.isArray(formData.categories) ? [...formData.categories] : [];
      
      // Update the category at the specified index
      const updatedCategories = [...currentCategories];
      if (index >= 0 && index < updatedCategories.length) {
        updatedCategories[index] = value;
      } else if (index === 0 && updatedCategories.length === 0) {
        // If the array is empty and we're trying to update the first item
        updatedCategories.push(value);
      }
      
      setFormData(prevData => ({
        ...prevData,
        categories: updatedCategories
      }));
    } catch (err) {
      console.error('Error changing category:', err);
      // Fallback to a safe operation
      setFormData(prevData => ({
        ...prevData,
        categories: [value]
      }));
    }
  };
  
  // Add a new category input field
  const handleAddCategory = () => {
    try {
      setFormData(prevData => {
        // Create a safe copy of the current categories
        const currentCategories = Array.isArray(prevData.categories) ? [...prevData.categories] : [];
        return {
          ...prevData,
          categories: [...currentCategories, ""]
        };
      });
    } catch (err) {
      console.error('Error adding category field:', err);
      // Fallback to a safe operation
      setFormData(prevData => ({
        ...prevData,
        categories: [""]
      }));
    }
  };
  
  // Remove a category input field
  const handleRemoveCategory = (index) => {
    try {
      // Create a safe copy of the current categories
      const currentCategories = Array.isArray(formData.categories) ? [...formData.categories] : [];
      
      // Only proceed if the index is valid
      if (index >= 0 && index < currentCategories.length) {
        const updatedCategories = [...currentCategories];
        updatedCategories.splice(index, 1);
        
        // Ensure at least one category field remains
        if (updatedCategories.length === 0) {
          updatedCategories.push("");
        }
        
        setFormData(prevData => ({
          ...prevData,
          categories: updatedCategories
        }));
      }
    } catch (err) {
      console.error('Error removing category:', err);
      // Fallback to a safe operation
      setFormData(prevData => ({
        ...prevData,
        categories: [""]
      }));
    }
  };
  
  // Add a predefined category
  const handleAddPredefinedCategory = (category) => {
    if (!category) return;
    
    try {
      // Create a safe copy of the current categories
      const currentCategories = Array.isArray(formData.categories) ? [...formData.categories] : [];
      
      // Check if category already exists
      if (!currentCategories.includes(category)) {
        const safeCategories = currentCategories.filter(c => typeof c === 'string' && c !== "");
        setFormData(prevData => ({
          ...prevData,
          categories: [...safeCategories, category]
        }));
      }
      setShowCategoryDropdown(null);
    } catch (err) {
      console.error('Error adding predefined category:', err);
      // Fallback to a safe operation
      setFormData(prevData => ({
        ...prevData,
        categories: [category]
      }));
      setShowCategoryDropdown(null);
    }
  };
  
  // Add a custom category
  const handleAddCustomCategory = () => {
    if (!customCategory || customCategory.trim() === "") return;
    
    try {
      // Convert to snake_case before adding
      const snakeCaseCategory = customCategory
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_');
      
      // Create a safe copy of the current categories
      const currentCategories = Array.isArray(formData.categories) ? [...formData.categories] : [];
      
      // Check if category already exists
      if (!currentCategories.includes(snakeCaseCategory)) {
        const safeCategories = currentCategories.filter(c => typeof c === 'string' && c !== "");
        setFormData(prevData => ({
          ...prevData,
          categories: [...safeCategories, snakeCaseCategory]
        }));
      }
      setCustomCategory("");
    } catch (err) {
      console.error('Error adding custom category:', err);
      // Fallback to a safe operation
      setFormData(prevData => ({
        ...prevData,
        categories: [customCategory.trim().toLowerCase().replace(/\s+/g, '_')]
      }));
      setCustomCategory("");
    }
  };
  
  // Handle form submission
  // Handle adding a new business type
  const handleAddBusinessType = async () => {
    if (!newBusinessType.trim()) return;
    
    setLoadingBusinessType(true);
    try {
      const newType = await addBusinessType(newBusinessType);
      setBusinessTypes([...businessTypes, newType]);
      setFormData({...formData, businessType: newType.id});
      setNewBusinessType("");
      setShowAddBusinessType(false);
    } catch (error) {
      setError("Failed to add business type. Please try again.");
    } finally {
      setLoadingBusinessType(false);
    }
  };
  
  // Handle adding a new business tag
  const handleAddBusinessTag = async () => {
    if (!newBusinessTag.trim() || !formData.businessType) return;
    
    setLoadingBusinessTag(true);
    try {
      // Pass the business type ID to the addBusinessTag function
      const newTag = await addBusinessTag(newBusinessTag, formData.businessType);
      setBusinessTags([...businessTags, newTag]);
      
      // If this tag is for the currently selected business type, add it to the specific tags list
      if (formData.businessType) {
        setBusinessTypeSpecificTags([...businessTypeSpecificTags, newTag]);
      }
      
      // Automatically select the new tag
      setFormData(prevData => ({
        ...prevData,
        businessTags: [...prevData.businessTags, newTag.id]
      }));
      
      setNewBusinessTag("");
    } catch (error) {
      console.error('Error adding business tag:', error);
      setError("Failed to add business tag. Please try again.");
    } finally {
      setLoadingBusinessTag(false);
    }
  };
  
  // Handle toggling a business tag selection
  const handleToggleTag = (tagId) => {
    setFormData(prevData => {
      const currentTags = [...prevData.businessTags];
      const tagIndex = currentTags.indexOf(tagId);
      
      if (tagIndex === -1) {
        // Add tag
        return {...prevData, businessTags: [...currentTags, tagId]};
      } else {
        // Remove tag
        currentTags.splice(tagIndex, 1);
        return {...prevData, businessTags: currentTags};
      }
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);
    setError(null);
    
    try {
      // Create a safe copy of the form data
      const safeFormData = {
        ...defaultFormData,
        ...formData
      };
      
      // For Excel integration, always set viewConsolidatedData to true
      if (safeFormData.useExcel) {
        safeFormData.viewConsolidatedData = true;
      }
      
      // Ensure all arrays are properly initialized
      const categories = Array.isArray(safeFormData.categories) ? safeFormData.categories : [];
      const hubspotSelectedCategories = Array.isArray(safeFormData.hubspotSelectedCategories) ? 
        safeFormData.hubspotSelectedCategories : [];
      
      // Prepare data for API with safe values
      const userData = {
        first_name: safeFormData.firstName || '',
        last_name: safeFormData.lastName || '',
        business_name: safeFormData.businessName || '',
        business_description: safeFormData.businessDescription || '',
        contact_phone: safeFormData.contactPhone || '',
        contact_email: safeFormData.contactEmail || '',
        business_website: safeFormData.businessWebsite || '',
        business_address: safeFormData.businessAddress || '',
        founded_year: safeFormData.foundedYear || '',
        business_type: safeFormData.businessType || '',
        categories: categories.filter(cat => typeof cat === 'string' && cat.trim() !== ""),
        whatsapp_phone_number_id: safeFormData.whatsappPhoneNumberId || '',
        whatsapp_business_account_id: safeFormData.whatsappBusinessAccountId || '',
        whatsapp_verify_token: safeFormData.whatsappVerifyToken || '',
        whatsapp_api_key: safeFormData.whatsappApiKey || '',
        whatsapp_app_id: safeFormData.whatsappAppId || '',
        whatsapp_app_secret: safeFormData.whatsappAppSecret || '',
        hubspot_access_token: safeFormData.hubspotAccessToken || '',
        hubspot_selected_categories: hubspotSelectedCategories,
        crm_type: safeFormData.crmType || 'hubspot',
        other_crm_details: safeFormData.otherCrmDetails || '',
        view_consolidated_data: Boolean(safeFormData.viewConsolidatedData),
        use_hubspot: Boolean(safeFormData.useHubspot),
        use_excel: Boolean(safeFormData.useExcel)
      };
      
      // Save settings and update business tags using Promise.allSettled to handle partial failures
      const [settingsResult, tagsResult] = await Promise.allSettled([
        updateUserSettings(user.id, userData),
        updateUserBusinessTags(user.id, safeFormData.businessTags || [])
      ]);
      
      // Check for errors in the results
      let hasErrors = false;
      let errorMessage = "";
      
      if (settingsResult.status === 'rejected' || (settingsResult.value && settingsResult.value.error)) {
        hasErrors = true;
        errorMessage += "Failed to save settings. ";
        console.error("Settings error:", settingsResult.status === 'rejected' ? settingsResult.reason : settingsResult.value.error);
      }
      
      if (tagsResult.status === 'rejected' || (tagsResult.value && tagsResult.value.error)) {
        hasErrors = true;
        errorMessage += "Failed to update business tags. ";
        console.error("Tags error:", tagsResult.status === 'rejected' ? tagsResult.reason : tagsResult.value.error);
      }
      
      if (hasErrors) {
        setError(errorMessage + "Please try again.");
      } else {
        setSuccess(true);
        
        // If we forced viewConsolidatedData to true for Excel, update the form state to match
        if (safeFormData.useExcel && !formData.viewConsolidatedData) {
          setFormData(safeFormData);
        }
        
        // Scroll to top to show success message
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          setSuccess(false);
        }, 3000);
      }
    } catch (err) {
      console.error("Error saving settings:", err);
      setError("Failed to save settings. Please check your network connection and try again.");
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <SignedIn>
        <DashboardHeader />
      </SignedIn>
      
      {/* Main content with top padding to account for fixed header */}
      <div className="min-h-screen bg-gray-50 pt-20 px-6 max-w-screen-2xl mx-auto">
        <h1 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Settings</h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 sm:px-4 sm:py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-3 py-2 sm:px-4 sm:py-3 rounded mb-4">
            Settings saved successfully!
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* User Information */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">User Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={userEmail}
                  disabled
                  className="w-full p-2 border border-gray-300 rounded bg-gray-100"
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>
            </div>
          </div>
          
          {/* Business Information */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Business Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Name
                </label>
                <input
                  type="text"
                  name="businessName"
                  value={formData.businessName}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Type
                </label>
                <div className="flex flex-col space-y-2">
                  <div className="relative">
                    <select
                      name="businessType"
                      value={formData.businessType}
                      onChange={(e) => {
                        handleInputChange(e);
                        setShowAddBusinessType(e.target.value === 'add_new');
                      }}
                      className="w-full p-2 border border-gray-300 rounded"
                    >
                      <option value="">Select a business type</option>
                      {businessTypes.map(type => (
                        <option key={type.id} value={type.id}>
                          {formatName(type.name)}
                        </option>
                      ))}
                      <option value="add_new">+ Add new business type</option>
                    </select>
                  </div>
                  
                  {showAddBusinessType && (
                    <div className="flex mt-2">
                      <input
                        type="text"
                        value={newBusinessType}
                        onChange={(e) => setNewBusinessType(e.target.value)}
                        placeholder="Enter new business type name"
                        className="flex-grow p-2 border border-gray-300 rounded-l"
                      />
                      <button
                        type="button"
                        onClick={handleAddBusinessType}
                        disabled={loadingBusinessType}
                        className={`px-4 py-2 ${loadingBusinessType ? 'bg-gray-400' : 'bg-pink-500 hover:bg-pink-600'} text-white rounded-r flex items-center`}
                      >
                        {loadingBusinessType ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Adding...
                          </>
                        ) : 'Add'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Description
                </label>
                <textarea
                  name="businessDescription"
                  value={formData.businessDescription}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full p-2 border border-gray-300 rounded"
                ></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Phone
                </label>
                <input
                  type="text"
                  name="contactPhone"
                  value={formData.contactPhone}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                <input
                  type="email"
                  name="contactEmail"
                  value={formData.contactEmail}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website
                </label>
                <input
                  type="url"
                  name="businessWebsite"
                  value={formData.businessWebsite}
                  onChange={handleInputChange}
                  placeholder="https://example.com"
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Year Founded
                </label>
                <input
                  type="text"
                  name="foundedYear"
                  value={formData.foundedYear}
                  onChange={handleInputChange}
                  placeholder="e.g. 2020"
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Address
                </label>
                <textarea
                  name="businessAddress"
                  value={formData.businessAddress}
                  onChange={handleInputChange}
                  rows="2"
                  className="w-full p-2 border border-gray-300 rounded"
                ></textarea>
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Tags
                </label>
                
                {formData.businessType ? (
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-600 mb-2">Suggested tags for this business type:</h4>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {businessTypeSpecificTags.length > 0 ? (
                        businessTypeSpecificTags.map(tag => (
                          <button
                            key={tag.id}
                            type="button"
                            onClick={() => handleToggleTag(tag.id)}
                            className={`px-3 py-1 rounded-full text-sm ${formData.businessTags.includes(tag.id) 
                              ? 'bg-pink-500 text-white' 
                              : 'bg-pink-100 text-pink-800 hover:bg-pink-200'}`}
                          >
                            {formatName(tag.name)}
                          </button>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500 italic">No suggested tags for this business type</p>
                      )}
                    </div>
                  </div>
                ) : null}
                
                {/* <h4 className="text-sm font-medium text-gray-600 mb-2">All available tags:</h4>
                <div className="flex flex-wrap gap-2 mb-2">
                  {businessTags.map(tag => (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => handleToggleTag(tag.id)}
                      className={`px-3 py-1 rounded-full text-sm ${formData.businessTags.includes(tag.id) 
                        ? 'bg-pink-500 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                    >
                      {formatName(tag.name)}
                    </button>
                  ))}
                </div> */}
                
                <div className="flex mt-2">
                  <input
                    type="text"
                    value={newBusinessTag}
                    onChange={(e) => setNewBusinessTag(e.target.value)}
                    placeholder="Add new business tag"
                    className="flex-grow p-2 border border-gray-300 rounded-l"
                  />
                  <button
                    type="button"
                    onClick={handleAddBusinessTag}
                    disabled={loadingBusinessTag}
                    className={`px-4 py-2 ${loadingBusinessTag ? 'bg-gray-400' : 'bg-pink-500 hover:bg-pink-600'} text-white rounded-r flex items-center`}
                  >
                    {loadingBusinessTag ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Adding...
                      </>
                    ) : 'Add'}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Categories */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Message Categories</h2>
            <p className="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
              Define categories for classifying customer messages. You can use our suggested categories or add your own.
            </p>
            
            {/* Category Reference */}
            <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-700 mb-2">Suggested Categories</h3>
              <div className="flex flex-wrap gap-1 sm:gap-2">
                {CATEGORY_OPTIONS.map(category => (
                  <button
                    key={category}
                    type="button"
                    onClick={() => handleAddPredefinedCategory(category)}
                    className="px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-sm hover:bg-pink-200"
                  >
                    {formatName(category)}
                  </button>
                ))}
              </div>
              <div className="mt-3 flex">
                <input
                  type="text"
                  value={customCategory}
                  onChange={(e) => setCustomCategory(e.target.value)}
                  placeholder="Add custom category"
                  className="p-2 border border-gray-300 rounded-l flex-grow"
                />
                <button
                  type="button"
                  onClick={handleAddCustomCategory}
                  className="bg-pink-500 text-white px-4 py-2 rounded-r hover:bg-pink-600"
                >
                  Add
                </button>
              </div>
            </div>
            
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Your Categories
              </label>
              
              {formData.categories.map((category, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={formatName(category)}
                    onChange={(e) => handleCategoryChange(index, e.target.value
                      .toLowerCase()
                      .replace(/\s+/g, '_')
                    )}
                    className="flex-grow p-2 border border-gray-300 rounded"
                    placeholder="Enter category name"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveCategory(index)}
                    className="p-2 text-red-500 hover:text-red-700"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              ))}
              
              <button
                type="button"
                onClick={handleAddCategory}
                className="mt-2 flex items-center text-pink-600 hover:text-pink-800"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 01-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Add Category
              </button>
            </div>
          </div>
          
          {/* WhatsApp Cloud API Settings */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">WhatsApp Cloud API Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  App ID
                </label>
                <input
                  type="text"
                  name="whatsappAppId"
                  value={formData.whatsappAppId}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Enter your Meta App ID"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  App Secret
                </label>
                <input
                  type="password"
                  name="whatsappAppSecret"
                  value={formData.whatsappAppSecret}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Enter your Meta App Secret"
                />
                <p className="text-xs text-gray-500 mt-1">Your app secret is stored securely</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number ID
                </label>
                <input
                  type="text"
                  name="whatsappPhoneNumberId"
                  value={formData.whatsappPhoneNumberId}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Enter your WhatsApp Phone Number ID"
                />
              </div>
              {/* Verify Token field removed as webhooks are set up through code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Verify Token
                </label>
                <div className="flex">
                  <input
                    type="text"
                    name="whatsappVerifyToken"
                    value={formData.whatsappVerifyToken}
                    onChange={handleInputChange}
                    className="w-full p-2 border border-gray-300 rounded-l"
                    placeholder="Enter your webhook verify token"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      // Generate a random verify token
                      const randomToken = Math.random().toString(36).substring(2, 15) + 
                                         Math.random().toString(36).substring(2, 15);
                      setFormData({...formData, whatsappVerifyToken: randomToken});
                    }}
                    className="bg-pink-500 text-white px-4 py-2 rounded-r hover:bg-pink-600"
                  >
                    Generate
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">This token is used to verify your webhook</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  WhatsApp Access Token
                </label>
                <input
                  type="password"
                  name="whatsappApiKey"
                  value={formData.whatsappApiKey}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Enter your WhatsApp API permanent access token"
                />
                <p className="text-xs text-gray-500 mt-1">Your access token is stored securely and encrypted</p>
              </div>
              
              {/* Interactive WhatsApp Cloud API Setup Guide */}
              <div className="mt-6 border-2 border-green-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-green-100 to-teal-100 px-4 py-3 flex items-center">
                  <svg className="h-6 w-6 mr-2" viewBox="0 0 24 24" fill="#25D366">
                    <path fillRule="evenodd" clipRule="evenodd" d="M17.415 14.382c-.298-.149-1.759-.867-2.031-.967-.272-.099-.47-.148-.669.15-.198.296-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.52.149-.174.198-.298.297-.497.1-.198.05-.371-.025-.52-.074-.149-.668-1.612-.916-2.207-.241-.579-.486-.5-.668-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.095 3.2 5.076 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.57-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" />
                    <path d="M12 22.5C17.5228 22.5 22 18.0228 22 12.5C22 6.97715 17.5228 2.5 12 2.5C6.47715 2.5 2 6.97715 2 12.5C2 14.6683 2.6424 16.6825 3.74685 18.3291L2.75 22.5L7.05 21.5613C8.62571 22.4225 10.4318 22.9178 12.3431 22.9944L12 22.5Z" stroke="#25D366" strokeWidth="1.5" />
                  </svg>
                  <h3 className="font-bold text-gray-800">WhatsApp Cloud API Quest</h3>
                </div>
                
                <div className="p-4 bg-white">
                  <div className="flex items-start mb-4">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Create Your Meta Developer Account</h4>
                      <p className="text-sm text-gray-600">Visit <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="text-green-500 hover:underline">developers.facebook.com</a> and sign up or log in</p>
                      <div className="mt-1 bg-gray-50 p-2 rounded border border-gray-200">
                        <span className="text-xs text-gray-500">💡 Tip: Use your business Facebook account if you have one</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Create a Meta App</h4>
                      <p className="text-sm text-gray-600">Click <span className="font-semibold text-green-600">"Create App"</span> and select <span className="font-mono bg-gray-100 px-1 rounded">Business</span> as the app type</p>
                      <div className="mt-2 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-500 mr-1" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <span className="text-xs text-gray-600">Name your app something related to your business (e.g., "YourBusiness WhatsApp")</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Add WhatsApp Product</h4>
                      <p className="text-sm text-gray-600">From your app dashboard, click <span className="font-semibold text-green-600">"Add Products"</span> and select <span className="font-mono bg-gray-100 px-1 rounded">WhatsApp</span></p>
                      <div className="mt-2 bg-green-50 p-2 rounded border border-green-200">
                        <div className="flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          <span className="text-xs font-semibold text-green-800">App ID & Secret:</span>
                        </div>
                        <span className="text-xs text-green-800">Find your App ID and App Secret in <span className="font-mono">App Dashboard → Settings → Basic</span></span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">4</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Set Up Your Phone Number</h4>
                      <p className="text-sm text-gray-600">Go to <span className="font-mono bg-gray-100 px-1 rounded">WhatsApp → Getting Started → Add Phone Number</span></p>
                      <div className="mt-2 flex flex-col space-y-2">
                        <div className="flex items-start">
                          <div className="min-w-[24px] h-6 flex items-center justify-center rounded-full bg-green-200 text-green-800 text-xs font-bold mr-2">A</div>
                          <span className="text-xs text-gray-600">You can use an existing business phone number or get a new one</span>
                        </div>
                        <div className="flex items-start">
                          <div className="min-w-[24px] h-6 flex items-center justify-center rounded-full bg-green-200 text-green-800 text-xs font-bold mr-2">B</div>
                          <span className="text-xs text-gray-600">Verify the phone number with the code sent via SMS</span>
                        </div>
                        <div className="flex items-start">
                          <div className="min-w-[24px] h-6 flex items-center justify-center rounded-full bg-green-200 text-green-800 text-xs font-bold mr-2">C</div>
                          <span className="text-xs text-gray-600">After verification, find your <span className="font-semibold">Phone Number ID</span> in the WhatsApp dashboard</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">5</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Generate a Long-Lived Access Token</h4>
                      <p className="text-sm text-gray-600">Generate a token using the <span className="font-mono bg-gray-100 px-1 rounded">Meta Graph API</span></p>
                      <div className="mt-2 bg-blue-50 p-2 rounded border border-blue-200">
                        <div className="flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          <span className="text-xs font-semibold text-blue-800">Token Generation Steps:</span>
                        </div>
                        <ul className="text-xs text-blue-800 list-disc pl-5 mt-1">
                          <li>Go to <a href="https://developers.facebook.com/tools/explorer/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Graph API Explorer</a></li>
                          <li>Select your app from the dropdown menu</li>
                          <li>Click <span className="font-semibold">"Generate Access Token"</span></li>
                          <li>Request the following permissions:
                            <ul className="list-disc pl-5 mt-1">
                              <li><span className="font-mono">whatsapp_business_messaging</span></li>
                              <li><span className="font-mono">whatsapp_business_management</span></li>
                              <li><span className="font-mono">business_management</span></li>
                            </ul>
                          </li>
                          <li>Once you have a short-lived token, use the <a href="https://developers.facebook.com/tools/debug/accesstoken/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Access Token Debugger</a> to extend it to a long-lived token</li>
                          <li>Copy the generated long-lived token to the <span className="font-semibold">WhatsApp Access Token</span> field above</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="bg-green-100 rounded-full p-2 mr-3">
                      <span className="text-green-600 font-bold">6</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Complete Your Setup</h4>
                      <p className="text-sm text-gray-600">Enter all the details in the form above and click "Save Settings"</p>
                      <div className="mt-2 bg-green-50 p-2 rounded border border-green-200">
                        <span className="text-xs text-green-800">🎉 Congratulations! Your WAffy dashboard is now connected to WhatsApp!</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 bg-teal-50 p-3 rounded-md border border-teal-100">
                <h4 className="font-medium text-teal-800 mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  Language Support
                </h4>
                <p className="text-xs text-teal-700 mb-2">Your WhatsApp integration supports 40+ global languages:</p>
                
                <div className="mb-3">
                  <h5 className="text-xs font-semibold text-teal-800 mb-1">Indian Languages:</h5>
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Hindi</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Tamil</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Telugu</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Bengali</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Marathi</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Gujarati</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Kannada</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Malayalam</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Punjabi</span>
                    <span className="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded-full">Odia</span>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-xs font-semibold text-teal-800 mb-1">Global Languages:</h5>
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">English</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Spanish</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">French</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">German</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Portuguese</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Italian</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Russian</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Japanese</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Korean</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Chinese</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Arabic</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Dutch</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Swedish</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Turkish</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Polish</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">+25 more</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* CRM Integration */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">CRM Integration</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select CRM Type
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 sm:gap-3">
                <div 
                  className={`p-3 sm:p-4 border rounded-md cursor-pointer flex flex-col items-center ${formData.crmType === 'hubspot' ? 'border-pink-500 bg-pink-50' : 'border-gray-300 hover:border-pink-300'}`}
                  onClick={() => setFormData({...formData, crmType: 'hubspot'})}
                >
                  <div className="w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center mb-2">
                  <svg height="2500" viewBox="6.20856283 .64498824 244.26943717 251.24701176" width="2500" xmlns="http://www.w3.org/2000/svg"><path d="m191.385 85.694v-29.506a22.722 22.722 0 0 0 13.101-20.48v-.677c0-12.549-10.173-22.722-22.721-22.722h-.678c-12.549 0-22.722 10.173-22.722 22.722v.677a22.722 22.722 0 0 0 13.101 20.48v29.506a64.342 64.342 0 0 0 -30.594 13.47l-80.922-63.03c.577-2.083.878-4.225.912-6.375a25.6 25.6 0 1 0 -25.633 25.55 25.323 25.323 0 0 0 12.607-3.43l79.685 62.007c-14.65 22.131-14.258 50.974.987 72.7l-24.236 24.243c-1.96-.626-4-.959-6.057-.987-11.607.01-21.01 9.423-21.007 21.03.003 11.606 9.412 21.014 21.018 21.017 11.607.003 21.02-9.4 21.03-21.007a20.747 20.747 0 0 0 -.988-6.056l23.976-23.985c21.423 16.492 50.846 17.913 73.759 3.562 22.912-14.352 34.475-41.446 28.985-67.918-5.49-26.473-26.873-46.734-53.603-50.792m-9.938 97.044a33.17 33.17 0 1 1 0-66.316c17.85.625 32 15.272 32.01 33.134.008 17.86-14.127 32.522-31.977 33.165" fill="#ff7a59"/></svg>
                </div>
                <span className="font-medium">HubSpot</span>
              </div>
              
              <div 
                className={`p-3 sm:p-4 border rounded-md cursor-pointer flex flex-col items-center ${formData.crmType === 'excel' ? 'border-pink-500 bg-pink-50' : 'border-gray-300 hover:border-pink-300'}`}
                onClick={() => setFormData({...formData, crmType: 'excel'})}
              >
                <div className="w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center mb-2">
                <svg viewBox="0 0 384 512" className="w-10 h-10 text-green-600" fill="currentColor">
                  <path d="m224 136V0H24C10.7 0 0 10.7 0 24v464c0 13.3 10.7 24 24 24h336c13.3 0 24-10.7 24-24V160H248c-13.2 0-24-10.8-24-24zm60.1 106.5L224 336l60.1 93.5c5.1 8-.6 18.5-10.1 18.5h-34.9c-4.4 0-8.5-2.4-10.6-6.3C208.9 405.5 192 373 192 373c-6.4 14.8-10 20-36.6 68.8-2.1 3.9-6.1 6.3-10.5 6.3H110c-9.5 0-15.2-10.5-10.1-18.5l60.3-93.5-60.3-93.5c-5.2-8 .6-18.5 10.1-18.5h34.8c4.4 0 8.5 2.4 10.6 6.3 26.1 48.8 20 33.6 36.6 68.5 0 0 6.1-11.7 36.6-68.5 2.1-3.9 6.2-6.3 10.6-6.3H274c9.5-.1 15.2 10.4 10.1 18.4z" />
                </svg>
                </div>
                <span className="font-medium">Excel</span>
              </div>
              
              <div 
                className={`p-3 sm:p-4 border rounded-md cursor-pointer flex flex-col items-center ${formData.crmType === 'other' ? 'border-pink-500 bg-pink-50' : 'border-gray-300 hover:border-pink-300'}`}
                onClick={() => setFormData({...formData, crmType: 'other'})}
              >
                <div className="w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center mb-2">
                <svg viewBox="0 0 512 512" className="w-10 h-10 text-blue-500" fill="currentColor">
                  <path d="M464 128H272l-64-64H48C21.49 64 0 85.49 0 112v288c0 26.51 21.49 48 48 48h416c26.51 0 48-21.49 48-48V176c0-26.51-21.49-48-48-48z" />
                </svg>
                </div>
                <span className="font-medium">Other CRM</span>
              </div>
            </div>
          </div>
          
          {/* HubSpot Integration Details */}
          {formData.crmType === 'hubspot' && (
            <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-700 mb-2">HubSpot Integration</h3>
              <p className="text-xs sm:text-sm text-gray-600 mb-4">
                Connect your HubSpot CRM to automatically sync customer data and conversations.
              </p>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Private App Access Token
                </label>
                <input
                  type="password"
                  name="hubspotAccessToken"
                  value={formData.hubspotAccessToken}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Enter your HubSpot Private App Access Token"
                />
              </div>
              
              <div className="mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="viewConsolidatedData"
                    checked={formData.viewConsolidatedData}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-pink-500 focus:ring-pink-400 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">View Consolidated Data on Dashboard</span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                When enabled, the enquiries, orders, issues, and feedback will be stored in the database and displayed on the dashboard.
                </p>
              </div>
              
              {/* Interactive HubSpot Token Guide */}
              <div className="mt-6 border-2 border-orange-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-orange-100 to-yellow-100 px-4 py-3 flex items-center">
                  <svg height="24" viewBox="6.20856283 .64498824 244.26943717 251.24701176" width="24" xmlns="http://www.w3.org/2000/svg" className="mr-2">
                    <path d="m191.385 85.694v-29.506a22.722 22.722 0 0 0 13.101-20.48v-.677c0-12.549-10.173-22.722-22.721-22.722h-.678c-12.549 0-22.722 10.173-22.722 22.722v.677a22.722 22.722 0 0 0 13.101 20.48v29.506a64.342 64.342 0 0 0 -30.594 13.47l-80.922-63.03c.577-2.083.878-4.225.912-6.375a25.6 25.6 0 1 0 -25.633 25.55 25.323 25.323 0 0 0 12.607-3.43l79.685 62.007c-14.65 22.131-14.258 50.974.987 72.7l-24.236 24.243c-1.96-.626-4-.959-6.057-.987-11.607.01-21.01 9.423-21.007 21.03.003 11.606 9.412 21.014 21.018 21.017 11.607.003 21.02-9.4 21.03-21.007a20.747 20.747 0 0 0 -.988-6.056l23.976-23.985c21.423 16.492 50.846 17.913 73.759 3.562 22.912-14.352 34.475-41.446 28.985-67.918-5.49-26.473-26.873-46.734-53.603-50.792m-9.938 97.044a33.17 33.17 0 1 1 0-66.316c17.85.625 32 15.272 32.01 33.134.008 17.86-14.127 32.522-31.977 33.165" fill="#ff7a59"/>
                  </svg>
                  <h3 className="font-bold text-gray-800">HubSpot Token Adventure</h3>
                </div>
                
                <div className="p-4 bg-white">
                  <div className="flex items-start mb-4">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Begin Your Quest</h4>
                      <p className="text-sm text-gray-600">Log in to your <a href="https://app.hubspot.com/" target="_blank" rel="noopener noreferrer" className="text-orange-500 hover:underline">HubSpot account</a> and prepare for an adventure!</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Find the Secret Portal</h4>
                      <p className="text-sm text-gray-600">Navigate to <span className="font-mono bg-gray-100 px-1 rounded">Settings → Integrations → Private Apps</span></p>
                      <div className="mt-1 bg-gray-50 p-2 rounded border border-gray-200">
                        <span className="text-xs text-gray-500">💡 Tip: Click the settings gear ⚙️ in the top right of your HubSpot dashboard</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Create Your Magic Key</h4>
                      <p className="text-sm text-gray-600">Click <span className="font-semibold text-green-600">"Create private app"</span> and name your app (e.g., "WAffy Integration")</p>
                      <div className="mt-2 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-500 mr-1" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <span className="text-xs text-gray-600">Add a description like "Integration between WAffy and HubSpot for WhatsApp message management"</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">4</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Choose Your Powers</h4>
                      <p className="text-sm text-gray-600">Select the scopes (permissions) needed based on your categories:</p>
                      
                      <div className="mt-2 space-y-2 text-sm">
                        <div className="flex items-center bg-green-50 p-2 rounded-md">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="font-mono text-xs text-green-800">crm.objects.contacts</span>
                          <span className="ml-2 text-xs text-gray-600">(Required for all categories)</span>
                        </div>
                        
                        {(formData.categories.includes('order_status') || formData.categories.includes('new_order')) && (
                          <div className="flex items-center bg-green-50 p-2 rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            <span className="font-mono text-xs text-green-800">crm.objects.deals</span>
                            <span className="ml-2 text-xs text-gray-600">(For order management)</span>
                          </div>
                        )}
                        
                        {(formData.categories.includes('complaint') || formData.categories.includes('return_refund')) && (
                          <div className="flex items-center bg-green-50 p-2 rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            <span className="font-mono text-xs text-green-800">crm.objects.tickets</span>
                            <span className="ml-2 text-xs text-gray-600">(For customer support)</span>
                          </div>
                        )}
                        
                        {formData.categories.includes('feedback') && (
                          <div className="flex items-center bg-green-50 p-2 rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            <span className="font-mono text-xs text-green-800">crm.objects.custom</span>
                            <span className="ml-2 text-xs text-gray-600">(For feedback tracking)</span>
                          </div>
                        )}
                        
                        <div className="flex items-center bg-green-50 p-2 rounded-md">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="font-mono text-xs text-green-800">crm.objects.owners</span>
                          <span className="ml-2 text-xs text-gray-600">(For assignment tracking)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start mb-4">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">5</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Claim Your Treasure</h4>
                      <p className="text-sm text-gray-600">Click <span className="font-semibold text-green-600">"Create app"</span> and copy your access token</p>
                      <div className="mt-2 bg-yellow-50 p-2 rounded border border-yellow-200">
                        <div className="flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-600 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          <span className="text-xs font-semibold text-yellow-800">Important:</span>
                        </div>
                        <span className="text-xs text-yellow-800">Copy your token immediately! It will only be shown once and looks like: <span className="font-mono bg-white px-1 rounded text-gray-600">pat-na1-12345...</span></span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="bg-orange-100 rounded-full p-2 mr-3">
                      <span className="text-orange-600 font-bold">6</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Complete Your Mission</h4>
                      <p className="text-sm text-gray-600">Paste the token in the field above and click "Save Settings"</p>
                      <div className="mt-2 bg-green-50 p-2 rounded border border-green-200">
                        <span className="text-xs text-green-800">🎉 Congratulations! Your WAffy dashboard is now connected to HubSpot!</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 bg-purple-50 p-3 rounded-md border border-purple-100">
                <h4 className="font-medium text-purple-800 mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  What can WAffy do with HubSpot?
                </h4>
                <ul className="text-xs text-purple-700 space-y-1 ml-6 list-disc">
                  <li>Create and update contacts from WhatsApp conversations</li>
                  <li>Generate tickets for customer issues and complaints</li>
                  <li>Track orders and create deals in your sales pipeline</li>
                  <li>Record customer feedback and satisfaction ratings</li>
                  <li>Maintain a complete history of customer interactions</li>
                </ul>
              </div>
            </div>
          )}
          
          {/* Excel Integration Details */}
          {formData.crmType === 'excel' && (
            <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-700 mb-2">Excel Integration</h3>
              <p className="text-xs sm:text-sm text-gray-600 mb-4">
                Export your WhatsApp messages and customer data to Excel spreadsheets.
              </p>
              
              <div className="mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={true}
                    disabled={true}
                    className="h-4 w-4 text-pink-500 focus:ring-pink-400 border-gray-300 rounded cursor-not-allowed bg-gray-200"
                  />
                  <span className="ml-2 text-sm text-gray-700">View Consolidated Data on Dashboard</span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                  Excel integration requires all messages to be stored in the database and displayed on the dashboard.
                </p>
              </div>
              
              <div className="text-xs sm:text-sm bg-blue-50 p-2 sm:p-3 rounded mt-4">
                <p>Excel integration allows you to export your data in various formats:</p>
                <ul className="list-disc pl-5 mt-1">
                  <li>Customer contact information</li>
                  <li>Message history and statistics</li>
                  <li>Category and tag reports</li>
                </ul>
                <p className="mt-2">You can configure export settings and schedules from the Export tab in the dashboard.</p>
              </div>
            </div>
          )}
          
          {/* Other CRM Integration Details */}
          {formData.crmType === 'other' && (
            <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-700 mb-2">Other CRM Integration</h3>
              <p className="text-xs sm:text-sm text-gray-600 mb-4">
                Provide details about your CRM system for custom integration.
              </p>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CRM Details
                </label>
                <textarea
                  name="otherCrmDetails"
                  value={formData.otherCrmDetails}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="Provide details about your CRM system (name, API endpoints, etc.)"
                ></textarea>
              </div>
              
              <div className="mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="viewConsolidatedData"
                    checked={formData.viewConsolidatedData}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-pink-500 focus:ring-pink-400 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">View Consolidated Data on Dashboard</span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                  When enabled, the enquiries, orders, issues, and feedback will be stored in the database and displayed on the dashboard.
                </p>
              </div>
            </div>
          )}
        </div>
        
        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className={`px-4 sm:px-6 py-2 rounded-md text-white ${
              loading ? "bg-gray-400" : "bg-gradient-to-r from-pink-500 to-yellow-500 hover:from-pink-600 hover:to-yellow-600"
            } transition-colors duration-300 flex items-center`}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
              </>
            ) : (
              "Save Settings"
            )}
          </button>
        </div>
      </form>
    </div>
  </>
)};

export default Settings;