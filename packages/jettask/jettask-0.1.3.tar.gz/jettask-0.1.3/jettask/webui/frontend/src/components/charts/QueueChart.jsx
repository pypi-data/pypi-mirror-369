import React from 'react';
import { Card, Empty } from 'antd';
import { Column } from '@ant-design/plots';

const QueueChart = ({ data, loading }) => {
  const config = {
    data: data || [],
    xField: 'name',
    yField: 'value',
    label: {
      position: 'middle',
      style: {
        fill: '#FFFFFF',
        opacity: 0.6,
      },
    },
    xAxis: {
      label: {
        autoHide: true,
        autoRotate: false,
      },
    },
    meta: {
      name: { alias: '队列' },
      value: { alias: '任务数' },
    },
  };

  return (
    <Card title="队列任务分布" loading={loading}>
      {data && data.length > 0 ? (
        <Column {...config} />
      ) : (
        <Empty description="暂无数据" />
      )}
    </Card>
  );
};

export default QueueChart;