import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Activity, ShieldCheck, Zap } from 'lucide-react';

export default function SalesTechB2BGrowthDashboard() {
  const [activeItems, setActiveItems] = useState(14);
  return (
    <div className='p-8 bg-slate-950 text-slate-100 min-h-screen'>
      <header className='mb-8 flex justify-between items-center'>
        <h1 className='text-2xl font-bold'>SalesTech / B2B Growth Command Center</h1>
        <Button className='bg-blue-600 hover:bg-blue-500'>+ New Scan</Button>
      </header>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <Card className='bg-slate-900 border-slate-800 p-6 rounded-2xl'>
          <CardTitle className='text-sm text-slate-400'>Domain Monitoring</CardTitle>
          <div className='text-3xl font-extrabold text-blue-400 mt-2'>{activeItems} Active</div>
        </Card>
      </div>
    </div>
  );
}
