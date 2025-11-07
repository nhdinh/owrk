import { useParams, Link } from 'react-router-dom';
import { useQuotationComparison } from '@/hooks/useQuotations';

export default function QuotationComparison() {
  const { prId } = useParams<{ prId: string }>();
  const { data, isLoading, error } = useQuotationComparison(prId!);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading quotation comparison
        </div>
      </div>
    );
  }

  const { purchase_request, quotations } = data;

  // Find the best price (lowest final amount)
  const bestPrice = quotations.length > 0
    ? Math.min(...quotations.map(q => q.final_amount))
    : 0;

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to={`/purchase-requests/${purchase_request.id}`} className="text-primary hover:underline text-sm">
          ← Back to Purchase Request
        </Link>
      </div>

      <div className="mb-6">
        <h1 className="text-3xl font-bold">Quotation Comparison</h1>
        <p className="text-muted-foreground mt-1">
          {purchase_request.request_code} - {purchase_request.title}
        </p>
      </div>

      {quotations.length === 0 ? (
        <div className="bg-card rounded-lg border p-12 text-center">
          <p className="text-muted-foreground text-lg mb-4">No quotations available for comparison</p>
          <Link
            to="/quotations/create"
            className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            Create Quotation
          </Link>
        </div>
      ) : (
        <>
          {/* Summary Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {quotations.map((quotation) => {
              const isBestPrice = quotation.final_amount === bestPrice;
              return (
                <div
                  key={quotation.id}
                  className={`bg-card rounded-lg border p-6 ${
                    isBestPrice ? 'ring-2 ring-green-500 bg-green-50' : ''
                  }`}
                >
                  {isBestPrice && (
                    <div className="bg-green-600 text-white text-xs font-bold px-2 py-1 rounded mb-3 inline-block">
                      BEST PRICE
                    </div>
                  )}

                  <h3 className="text-xl font-bold mb-2">{quotation.vendor.name}</h3>

                  {quotation.vendor.rating && (
                    <div className="flex items-center gap-1 mb-3">
                      <span className="text-yellow-500">★</span>
                      <span className="text-sm font-medium">{quotation.vendor.rating.toFixed(1)}</span>
                    </div>
                  )}

                  <div className="space-y-2 mb-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Final Amount</p>
                      <p className={`text-2xl font-bold ${isBestPrice ? 'text-green-700' : ''}`}>
                        ${quotation.final_amount.toFixed(2)}
                      </p>
                    </div>

                    {quotation.valid_until && (
                      <div>
                        <p className="text-sm text-muted-foreground">Valid Until</p>
                        <p className="font-medium">{new Date(quotation.valid_until).toLocaleDateString()}</p>
                      </div>
                    )}

                    {quotation.delivery_terms && (
                      <div>
                        <p className="text-sm text-muted-foreground">Delivery</p>
                        <p className="text-sm">{quotation.delivery_terms}</p>
                      </div>
                    )}

                    {quotation.warranty_terms && (
                      <div>
                        <p className="text-sm text-muted-foreground">Warranty</p>
                        <p className="text-sm">{quotation.warranty_terms}</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Link
                      to={`/quotations/${quotation.id}`}
                      className="block w-full px-4 py-2 text-center border rounded-lg hover:bg-muted"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detailed Items Comparison Table */}
          <div className="bg-card rounded-lg border overflow-hidden">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">Items Comparison</h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium">Vendor</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Product</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Qty</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Unit</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Unit Price</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {quotations.map((quotation) => (
                    <React.Fragment key={quotation.id}>
                      {quotation.items.map((item, itemIndex) => (
                        <tr
                          key={`${quotation.id}-${itemIndex}`}
                          className={`border-t ${
                            quotation.final_amount === bestPrice ? 'bg-green-50' : ''
                          }`}
                        >
                          {itemIndex === 0 && (
                            <td
                              className="px-4 py-3 font-medium align-top"
                              rowSpan={quotation.items.length}
                            >
                              <div className="flex items-center gap-2">
                                {quotation.vendor.name}
                                {quotation.final_amount === bestPrice && (
                                  <span className="text-xs bg-green-600 text-white px-1.5 py-0.5 rounded">
                                    Best
                                  </span>
                                )}
                              </div>
                            </td>
                          )}
                          <td className="px-4 py-3">
                            <div>
                              <p className="font-medium">{item.product_name}</p>
                              {item.product_description && (
                                <p className="text-sm text-muted-foreground">{item.product_description}</p>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right">{item.quantity}</td>
                          <td className="px-4 py-3">{item.unit}</td>
                          <td className="px-4 py-3 text-right">${item.unit_price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right font-medium">${item.total_price.toFixed(2)}</td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recommendation */}
          <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-900 mb-2">Recommendation</h3>
            <p className="text-green-700 mb-4">
              Based on price comparison, <strong>{quotations.find(q => q.final_amount === bestPrice)?.vendor.name}</strong> offers
              the best price at <strong>${bestPrice.toFixed(2)}</strong>.
            </p>
            <p className="text-sm text-green-600">
              Please also consider delivery terms, warranty, and vendor rating before making a final decision.
            </p>
          </div>
        </>
      )}
    </div>
  );
}

// Add React import for Fragment
import React from 'react';
