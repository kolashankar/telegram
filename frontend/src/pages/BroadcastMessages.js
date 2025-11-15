import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Send, 
  Users, 
  MessageSquare,
  Clock,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BroadcastMessages = () => {
  const [message, setMessage] = useState('');
  const [target, setTarget] = useState('all');
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchBroadcasts();
  }, []);

  const fetchBroadcasts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/broadcasts`);
      setBroadcasts(response.data.broadcasts || []);
    } catch (error) {
      console.error('Error fetching broadcasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendBroadcast = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) {
      alert('Please enter a message');
      return;
    }

    if (!window.confirm(`Send this message to ${target} users?`)) return;

    try {
      setSending(true);
      const response = await axios.post(`${API}/admin/broadcast`, {
        message: message.trim(),
        target: target
      });
      
      alert(`Broadcast queued! Will be sent to ${response.data.recipient_count} users.`);
      setMessage('');
      fetchBroadcasts();
    } catch (error) {
      console.error('Error sending broadcast:', error);
      alert(error.response?.data?.detail || 'Failed to send broadcast');
    } finally {
      setSending(false);
    }
  };

  const targetOptions = [
    { value: 'all', label: 'All Users', icon: Users, description: 'Send to everyone' },
    { value: 'active', label: 'Active Subscribers', icon: CheckCircle, description: 'Users with active subscriptions' },
    { value: 'expired', label: 'Expired/No Subscription', icon: Clock, description: 'Users without active subscriptions' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Broadcast Messages</h1>
        <p className="text-gray-600 mt-1">Send announcements to your bot users</p>
      </div>

      {/* Send Broadcast Form */}
      <Card>
        <CardHeader>
          <CardTitle>Create Broadcast</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={sendBroadcast} className="space-y-6">
            {/* Target Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Target Audience
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {targetOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      target === option.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setTarget(option.value)}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        target === option.value ? 'bg-blue-500' : 'bg-gray-200'
                      }`}>
                        <option.icon className={`w-5 h-5 ${
                          target === option.value ? 'text-white' : 'text-gray-600'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <p className={`font-semibold ${
                          target === option.value ? 'text-blue-900' : 'text-gray-900'
                        }`}>
                          {option.label}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">{option.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Message Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your announcement message here..."
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                required
              />
              <div className="flex justify-between items-center mt-2">
                <p className="text-sm text-gray-500">
                  {message.length} characters
                </p>
              </div>
            </div>

            {/* Preview */}
            {message.trim() && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900 mb-1">OTT Bot Admin</p>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{message}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={sending || !message.trim()}
            >
              {sending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Send Broadcast
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Broadcast History */}
      <Card>
        <CardHeader>
          <CardTitle>Broadcast History</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : broadcasts.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No broadcasts sent yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {broadcasts.map((broadcast, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <MessageSquare className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 line-clamp-2 mb-2">
                          {broadcast.message}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {broadcast.recipient_count} recipients
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(broadcast.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge 
                        className={
                          broadcast.status === 'sent' ? 'bg-green-500' :
                          broadcast.status === 'queued' ? 'bg-yellow-500' :
                          'bg-gray-500'
                        }
                      >
                        {broadcast.status || 'queued'}
                      </Badge>
                      <span className="text-xs text-gray-500 capitalize">
                        Target: {broadcast.target}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BroadcastMessages;
