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
  
  // Form state
  const [formData, setFormData] = useState({
    // User Info
    firstName: "",
    lastName: "",
    
    // Basic Business Info
    businessName: "",
    businessDescription: "",
    contactPhone: "",
    contactEmail: "",
    businessAddress: "",
    businessWebsite: "",
    businessType: "", // Will be the selected business type ID
    businessTags: [], // Will store selected tag IDs
    foundedYear: "",
    
    // Product/Service Categories
    categories: [""],
    
    // WhatsApp Cloud API Settings
    whatsappAppId: "",
    whatsappAppSecret: "",
    whatsappPhoneNumberId: "",
    whatsappVerifyToken: "",
    
    // CRM Integration
    crmType: "hubspot", // hubspot, excel, other
    hubspotAccessToken: "",
    otherCrmDetails: "",
    
    // Dashboard Settings
    viewConsolidatedData: false
  });

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
          
          // Handle business tags result
          if (userTagsResult.status === 'fulfilled' && userTagsResult.value && Array.isArray(userTagsResult.value)) {
            setUserBusinessTags(userTagsResult.value);
          }
          
          // Get the settings from the result
          const userSettings = userSettingsResult.status === 'fulfilled' ? userSettingsResult.value : null;
          
          if (userSettings) {
            if (userSettings.message) {
              // Show error message to the user
              setError(userSettings.message);
              
              // Still populate form with Clerk user data
              setFormData(prevData => ({
                ...prevData,
                firstName: user.firstName || "",
                lastName: user.lastName || "",
                categories: [""]
              }));
              
              console.log("Error loading settings:", userSettings.message);
            } else {
              // Map backend settings to form data
              setFormData({
                firstName: userSettings.first_name || "",
                lastName: userSettings.last_name || "",
                businessName: userSettings.business_name || "",
                businessDescription: userSettings.business_description || "",
                contactPhone: userSettings.contact_phone || "",
                contactEmail: userSettings.contact_email || "",
                businessAddress: userSettings.business_address || "",
                businessWebsite: userSettings.business_website || "",
                businessType: userSettings.business_type || "",
                foundedYear: userSettings.founded_year || "",
                categories: userSettings.categories?.length ? userSettings.categories : [""],
                whatsappAppId: userSettings.whatsapp_app_id || "",
                whatsappAppSecret: userSettings.whatsapp_api_key || "", // Note: API key is stored as app secret
                whatsappPhoneNumberId: userSettings.whatsapp_phone_number_id || "",
                whatsappVerifyToken: userSettings.whatsapp_verify_token || "",
                crmType: userSettings.crm_type || "hubspot",
                hubspotAccessToken: userSettings.hubspot_api_key || "", // Note: API key is stored as access token
                otherCrmDetails: userSettings.other_crm_details || "",
                businessTags: userBusinessTags.map(tag => tag.id) || [],
                viewConsolidatedData: userSettings.view_consolidated_data || false
              });
              console.log("Loaded settings from database");
            }
          } else {
            // No settings found, use defaults with Clerk user data
            setFormData(prevData => ({
              ...prevData,
              firstName: user.firstName || "",
              lastName: user.lastName || "",
              // Ensure categories array has at least 1 item
              categories: [""]
            }));
            
            console.log("Using default settings");
          }
        } catch (error) {
          console.error("Error fetching user data:", error);
          // Fallback to Clerk email and default settings
          setUserEmail(user.primaryEmailAddress?.emailAddress || "");
          setFormData(prevData => ({
            ...prevData,
            firstName: user.firstName || "",
            lastName: user.lastName || "",
            categories: [""]
          }));
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
    const updatedCategories = [...formData.categories];
    updatedCategories[index] = value;
    
    setFormData(prevData => ({
      ...prevData,
      categories: updatedCategories
    }));
  };
  
  // Add a new category input field
  const handleAddCategory = () => {
    setFormData(prevData => ({
      ...prevData,
      categories: [...prevData.categories, ""]
    }));
  };
  
  // Remove a category input field
  const handleRemoveCategory = (index) => {
    const updatedCategories = [...formData.categories];
    updatedCategories.splice(index, 1);
    
    // Ensure at least one category field remains
    if (updatedCategories.length === 0) {
      updatedCategories.push("");
    }
    
    setFormData(prevData => ({
      ...prevData,
      categories: updatedCategories
    }));
  };
  
  // Add a predefined category
  const handleAddPredefinedCategory = (category) => {
    // Check if category already exists
    if (!formData.categories.includes(category)) {
      setFormData(prevData => ({
        ...prevData,
        categories: [...prevData.categories.filter(c => c !== ""), category]
      }));
    }
    setShowCategoryDropdown(null);
  };
  
  // Add a custom category
  const handleAddCustomCategory = () => {
    if (customCategory.trim() !== "") {
      // Convert to snake_case before adding
      const snakeCaseCategory = customCategory
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_');
      if (!formData.categories.includes(snakeCaseCategory)) {
        setFormData(prevData => ({
          ...prevData,
          categories: [
            ...prevData.categories.filter(c => c !== ""),
            snakeCaseCategory
          ]
        }));
      }
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
      // For Excel integration, always set viewConsolidatedData to true
      let updatedFormData = {...formData};
      if (formData.crmType === 'excel') {
        updatedFormData.viewConsolidatedData = true;
      }
      
      // Prepare data for API
      const userData = {
        first_name: updatedFormData.firstName,
        last_name: updatedFormData.lastName,
        business_name: updatedFormData.businessName,
        business_description: updatedFormData.businessDescription,
        contact_phone: updatedFormData.contactPhone,
        contact_email: updatedFormData.contactEmail,
        business_address: updatedFormData.businessAddress,
        business_website: updatedFormData.businessWebsite,
        business_type: updatedFormData.businessType,
        founded_year: updatedFormData.foundedYear,
        categories: updatedFormData.categories.filter(cat => cat.trim() !== ""),
        whatsapp_app_id: updatedFormData.whatsappAppId,
        whatsapp_app_secret: updatedFormData.whatsappAppSecret,
        whatsapp_phone_number_id: updatedFormData.whatsappPhoneNumberId,
        whatsapp_verify_token: updatedFormData.whatsappVerifyToken,
        crm_type: updatedFormData.crmType,
        hubspot_access_token: updatedFormData.hubspotAccessToken,
        other_crm_details: updatedFormData.otherCrmDetails,
        view_consolidated_data: updatedFormData.viewConsolidatedData
      };
      
      // Save settings and update business tags using Promise.allSettled to handle partial failures
      const [settingsResult, tagsResult] = await Promise.allSettled([
        updateUserSettings(user.id, userData),
        updateUserBusinessTags(user.id, updatedFormData.businessTags)
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
        if (formData.crmType === 'excel' && !formData.viewConsolidatedData) {
          setFormData(updatedFormData);
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
              
              <div className="mt-3 text-sm bg-blue-50 p-3 rounded">
                <p className="font-medium text-blue-800">How to set up WhatsApp Cloud API:</p>
                <ol className="list-decimal pl-5 mt-1 text-blue-800">
                  <li>Create a Meta Developer account at <a href="https://developers.facebook.com/" className="underline" target="_blank" rel="noopener noreferrer">developers.facebook.com</a></li>
                  <li>Create a Meta App and set up WhatsApp Business Platform</li>
                  <li>Get your App ID and App Secret from the App Dashboard</li>
                  <li>Add a WhatsApp phone number to your app</li>
                  <li>Get your Phone Number ID from the WhatsApp → API Setup page</li>
                  <li>Generate a Verify Token (or use the button above) for webhook setup</li>
                  <li>Configure your webhook URL as: <code className="bg-blue-100 px-1 rounded">https://your-domain.com/api/webhook/whatsapp</code></li>
                </ol>
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
              
              <div className="text-xs sm:text-sm bg-blue-50 p-2 sm:p-3 rounded mt-4">
                <p className="font-medium text-blue-800">How to get your HubSpot Private App Access Token:</p>
                <ol className="list-decimal pl-5 mt-1 text-blue-800">
                  <li>Go to your HubSpot account</li>
                  <li>Navigate to Settings → Integrations → Private Apps</li>
                  <li>Click "Create private app"</li>
                  <li>Name your app (e.g., "WAffy Integration")</li>
                  <li>Select scopes for contacts, tickets, and other required data</li>
                  <li>Create the app and copy your access token</li>
                </ol>
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