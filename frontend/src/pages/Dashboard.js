import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, DollarSign, Clock, TrendingUp, Activity } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/statistics`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'bg-blue-500',
      trend: `+${stats?.new_users_this_week || 0} this week`
    },
    {
      title: 'Active Subscriptions',
      value: stats?.active_users || 0,
      icon: Activity,
      color: 'bg-green-500',
      trend: 'Currently active'
    },
    {
      title: 'Total Revenue',
      value: `₹${stats?.total_revenue?.toLocaleString() || 0}`,
      icon: DollarSign,
      color: 'bg-purple-500',
      trend: 'All time'
    },
    {
      title: 'Pending Payments',
      value: stats?.pending_payments || 0,
      icon: Clock,
      color: 'bg-orange-500',
      trend: 'Awaiting approval'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your Telegram bot statistics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <h3 className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</h3>
                  <p className="text-xs text-gray-500 mt-1">{stat.trend}</p>
                </div>
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Revenue by Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Plan Type</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.revenue_by_plan?.length > 0 ? (
              <div className="space-y-4">
                {stats.revenue_by_plan.map((plan, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 capitalize">{plan._id || 'Unknown'}</p>
                      <p className="text-sm text-gray-600">{plan.count} subscriptions</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900">₹{plan.total.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No revenue data available</p>
            )}
          </CardContent>
        </Card>

        {/* Top Platforms */}
        <Card>
          <CardHeader>
            <CardTitle>Top OTT Platforms</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.top_platforms?.length > 0 ? (
              <div className="space-y-3">
                {stats.top_platforms.slice(0, 5).map((platform, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                        {index + 1}
                      </div>
                      <span className="font-medium text-gray-900">{platform.platform}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{platform.users} users</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${(platform.users / stats.active_users) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No platform data available</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
