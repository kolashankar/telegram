import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Search, 
  Filter, 
  Eye, 
  Trash2, 
  UserCheck, 
  UserX,
  Calendar,
  DollarSign
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetails, setUserDetails] = useState(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [statusFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100,
        skip: 0
      };
      
      if (search) params.search = search;
      if (statusFilter !== 'all') params.status = statusFilter;

      const response = await axios.get(`${API}/admin/users`, { params });
      setUsers(response.data.users || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetails = async (telegramId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${telegramId}`);
      setUserDetails(response.data);
      setSelectedUser(telegramId);
    } catch (error) {
      console.error('Error fetching user details:', error);
    }
  };

  const deleteUser = async (telegramId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await axios.delete(`${API}/admin/users/${telegramId}`);
      fetchUsers();
      setSelectedUser(null);
      setUserDetails(null);
    } catch (error) {
      console.error('Error deleting user:', error);
      alert('Failed to delete user');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers();
  };

  const hasActiveSubscription = (user) => {
    return user.active_subscriptions && user.active_subscriptions.length > 0;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="text-gray-600 mt-1">Manage and monitor all bot users</p>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <form onSubmit={handleSearch} className="flex-1 flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by username, name, or Telegram ID..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <Button type="submit">Search</Button>
            </form>
            
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Users</option>
                <option value="active">Active Subscriptions</option>
                <option value="expired">Expired/No Subscription</option>
              </select>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            Showing {users.length} of {total} users
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Users Table */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Users</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : users.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No users found
                </div>
              ) : (
                <div className="space-y-3">
                  {users.map((user) => (
                    <div
                      key={user.telegram_id}
                      className={`p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer ${
                        selectedUser === user.telegram_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                      onClick={() => fetchUserDetails(user.telegram_id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 font-bold">
                                {user.first_name?.[0] || 'U'}
                              </span>
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">
                                {user.first_name || 'Unknown'} {user.last_name || ''}
                              </p>
                              <p className="text-sm text-gray-600">
                                @{user.telegram_username || user.telegram_id}
                              </p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          {hasActiveSubscription(user) ? (
                            <Badge className="bg-green-500">
                              <UserCheck className="w-3 h-3 mr-1" />
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="secondary">
                              <UserX className="w-3 h-3 mr-1" />
                              Inactive
                            </Badge>
                          )}
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchUserDetails(user.telegram_id);
                            }}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      {hasActiveSubscription(user) && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              <span>
                                Expires: {new Date(user.active_subscriptions[0].expiry_date).toLocaleDateString()}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              <span>₹{user.total_spent || 0}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* User Details Panel */}
        <div className="lg:col-span-1">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>User Details</CardTitle>
            </CardHeader>
            <CardContent>
              {!userDetails ? (
                <div className="text-center py-12 text-gray-500">
                  <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>Select a user to view details</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-center pb-4 border-b border-gray-200">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-blue-600 font-bold text-2xl">
                        {userDetails.user.first_name?.[0] || 'U'}
                      </span>
                    </div>
                    <h3 className="font-bold text-lg text-gray-900">
                      {userDetails.user.first_name || 'Unknown'} {userDetails.user.last_name || ''}
                    </h3>
                    <p className="text-sm text-gray-600">@{userDetails.user.telegram_username || userDetails.user.telegram_id}</p>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-gray-600">Telegram ID</p>
                      <p className="font-semibold text-gray-900">{userDetails.user.telegram_id}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-600">Total Spent</p>
                      <p className="font-semibold text-gray-900">₹{userDetails.user.total_spent || 0}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-600">Member Since</p>
                      <p className="font-semibold text-gray-900">
                        {new Date(userDetails.user.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-600">Last Active</p>
                      <p className="font-semibold text-gray-900">
                        {new Date(userDetails.user.last_active).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Subscriptions */}
                  <div className="pt-4 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-3">Active Subscriptions</h4>
                    {userDetails.user.active_subscriptions?.length > 0 ? (
                      <div className="space-y-2">
                        {userDetails.user.active_subscriptions.map((sub, index) => (
                          <div key={index} className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm">
                            <p className="font-semibold text-green-900 capitalize">{sub.plan_type}</p>
                            <p className="text-green-700">
                              Expires: {new Date(sub.expiry_date).toLocaleDateString()}
                            </p>
                            <p className="text-green-600">₹{sub.amount_paid}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No active subscriptions</p>
                    )}
                  </div>

                  {/* Payment History */}
                  <div className="pt-4 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-3">Payment History</h4>
                    {userDetails.payments?.length > 0 ? (
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {userDetails.payments.map((payment, index) => (
                          <div key={index} className="p-2 bg-gray-50 rounded text-xs">
                            <div className="flex justify-between items-center">
                              <span className="font-semibold">₹{payment.amount}</span>
                              <Badge 
                                className={
                                  payment.status === 'verified' ? 'bg-green-500' :
                                  payment.status === 'pending' ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }
                              >
                                {payment.status}
                              </Badge>
                            </div>
                            <p className="text-gray-600 mt-1">
                              {new Date(payment.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No payment history</p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="pt-4 border-t border-gray-200">
                    <Button
                      variant="destructive"
                      className="w-full"
                      onClick={() => deleteUser(userDetails.user.telegram_id)}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete User
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
