import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye,
  DollarSign,
  Calendar,
  User
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentManagement = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [total, setTotal] = useState(0);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchPayments();
  }, [statusFilter]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100,
        skip: 0
      };
      
      if (statusFilter !== 'all') params.status = statusFilter;

      const response = await axios.get(`${API}/admin/payments`, { params });
      setPayments(response.data.payments || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching payments:', error);
    } finally {
      setLoading(false);
    }
  };

  const approvePayment = async (paymentId) => {
    if (!window.confirm('Approve this payment and activate subscription?')) return;
    
    try {
      setProcessing(true);
      await axios.put(`${API}/admin/payments/${paymentId}/approve`);
      await fetchPayments();
      setSelectedPayment(null);
      alert('Payment approved successfully!');
    } catch (error) {
      console.error('Error approving payment:', error);
      alert(error.response?.data?.detail || 'Failed to approve payment');
    } finally {
      setProcessing(false);
    }
  };

  const rejectPayment = async (paymentId) => {
    const reason = window.prompt('Enter rejection reason:');
    if (!reason) return;
    
    try {
      setProcessing(true);
      await axios.put(`${API}/admin/payments/${paymentId}/reject`, null, {
        params: { reason }
      });
      await fetchPayments();
      setSelectedPayment(null);
      alert('Payment rejected');
    } catch (error) {
      console.error('Error rejecting payment:', error);
      alert('Failed to reject payment');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-500', icon: Clock },
      verified: { color: 'bg-green-500', icon: CheckCircle },
      rejected: { color: 'bg-red-500', icon: XCircle }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;
    
    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Payment Management</h1>
        <p className="text-gray-600 mt-1">Review and approve user payments</p>
      </div>

      {/* Filter */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <Button
                variant={statusFilter === 'pending' ? 'default' : 'outline'}
                onClick={() => setStatusFilter('pending')}
              >
                <Clock className="w-4 h-4 mr-2" />
                Pending
              </Button>
              <Button
                variant={statusFilter === 'verified' ? 'default' : 'outline'}
                onClick={() => setStatusFilter('verified')}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Approved
              </Button>
              <Button
                variant={statusFilter === 'rejected' ? 'default' : 'outline'}
                onClick={() => setStatusFilter('rejected')}
              >
                <XCircle className="w-4 h-4 mr-2" />
                Rejected
              </Button>
              <Button
                variant={statusFilter === 'all' ? 'default' : 'outline'}
                onClick={() => setStatusFilter('all')}
              >
                All
              </Button>
            </div>
            
            <div className="text-sm text-gray-600">
              {total} {statusFilter !== 'all' ? statusFilter : ''} payments
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payments Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Payments List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Payments</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : payments.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No {statusFilter !== 'all' ? statusFilter : ''} payments found
                </div>
              ) : (
                <div className="space-y-3">
                  {payments.map((payment) => (
                    <div
                      key={payment.payment_id}
                      className={`p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer ${
                        selectedPayment?.payment_id === payment.payment_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                      onClick={() => setSelectedPayment(payment)}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-lg flex items-center justify-center">
                            <DollarSign className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <p className="font-bold text-lg text-gray-900">₹{payment.amount}</p>
                            <p className="text-sm text-gray-600 capitalize">{payment.plan_type}</p>
                          </div>
                        </div>
                        {getStatusBadge(payment.status)}
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="flex items-center gap-2 text-gray-600">
                          <User className="w-4 h-4" />
                          <span>User: {payment.telegram_id}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(payment.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {payment.platforms && payment.platforms.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-600 mb-2">Platforms:</p>
                          <div className="flex flex-wrap gap-1">
                            {payment.platforms.slice(0, 5).map((platform, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                                {platform}
                              </span>
                            ))}
                            {payment.platforms.length > 5 && (
                              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                +{payment.platforms.length - 5} more
                              </span>
                            )}
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

        {/* Payment Details Panel */}
        <div className="lg:col-span-1">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>Payment Details</CardTitle>
            </CardHeader>
            <CardContent>
              {!selectedPayment ? (
                <div className="text-center py-12 text-gray-500">
                  <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>Select a payment to view details</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Amount */}
                  <div className="text-center pb-4 border-b border-gray-200">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-3">
                      <DollarSign className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-3xl font-bold text-gray-900">₹{selectedPayment.amount}</h3>
                    <p className="text-sm text-gray-600 mt-1 capitalize">{selectedPayment.plan_type} Plan</p>
                    {getStatusBadge(selectedPayment.status)}
                  </div>

                  {/* Details */}
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-gray-600">Payment ID</p>
                      <p className="font-mono text-xs text-gray-900 break-all">{selectedPayment.payment_id}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-600">User ID (Telegram)</p>
                      <p className="font-semibold text-gray-900">{selectedPayment.telegram_id}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-600">UPI ID</p>
                      <p className="font-semibold text-gray-900">{selectedPayment.upi_id}</p>
                    </div>
                    
                    {selectedPayment.transaction_id && (
                      <div>
                        <p className="text-gray-600">Transaction ID</p>
                        <p className="font-semibold text-gray-900">{selectedPayment.transaction_id}</p>
                      </div>
                    )}
                    
                    <div>
                      <p className="text-gray-600">Created At</p>
                      <p className="font-semibold text-gray-900">
                        {new Date(selectedPayment.created_at).toLocaleString()}
                      </p>
                    </div>

                    {selectedPayment.verification_date && (
                      <div>
                        <p className="text-gray-600">Verification Date</p>
                        <p className="font-semibold text-gray-900">
                          {new Date(selectedPayment.verification_date).toLocaleString()}
                        </p>
                      </div>
                    )}

                    {selectedPayment.rejection_reason && (
                      <div>
                        <p className="text-gray-600">Rejection Reason</p>
                        <p className="font-semibold text-red-600">{selectedPayment.rejection_reason}</p>
                      </div>
                    )}
                  </div>

                  {/* Platforms */}
                  {selectedPayment.platforms && selectedPayment.platforms.length > 0 && (
                    <div className="pt-4 border-t border-gray-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Platforms ({selectedPayment.platforms.length})</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedPayment.platforms.map((platform, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                            {platform}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Screenshot */}
                  {selectedPayment.screenshot_url && (
                    <div className="pt-4 border-t border-gray-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Payment Screenshot</h4>
                      <img 
                        src={selectedPayment.screenshot_url} 
                        alt="Payment proof" 
                        className="w-full rounded-lg border border-gray-200"
                      />
                    </div>
                  )}

                  {/* Actions for Pending Payments */}
                  {selectedPayment.status === 'pending' && (
                    <div className="pt-4 border-t border-gray-200 space-y-2">
                      <Button
                        className="w-full bg-green-600 hover:bg-green-700"
                        onClick={() => approvePayment(selectedPayment.payment_id)}
                        disabled={processing}
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        {processing ? 'Processing...' : 'Approve Payment'}
                      </Button>
                      
                      <Button
                        variant="destructive"
                        className="w-full"
                        onClick={() => rejectPayment(selectedPayment.payment_id)}
                        disabled={processing}
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject Payment
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PaymentManagement;
