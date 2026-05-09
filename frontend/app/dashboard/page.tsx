'use client'

import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { io } from 'socket.io-client'
import { AppDispatch, RootState } from '../../store'
import { addMetric, clearMetrics } from '../../store/metricsSlice'

const LineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false })
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false })
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false })
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false })
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false })
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false })
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false })

export default function Dashboard() {
  const dispatch = useDispatch<AppDispatch>()
  const metrics = useSelector((state: RootState) => state.metrics.data)
  const experimentGroups = metrics.reduce((acc, m) => {
    if (!acc[m.experiment_id]) acc[m.experiment_id] = []
    acc[m.experiment_id].push(m)
    return acc
  }, {} as Record<string, typeof metrics>)
  const [inference, setInference] = useState<{
    prediction: number
    latency_ms: number
    cpu_temp: number
  } | null>(null)
  const [imu, setImu] = useState<{
    accel_x: number
    accel_y: number
    accel_z: number
    gyro_x: number
    gyro_y: number
    gyro_z: number
  } | null>(null)

  useEffect(() => {
    dispatch(clearMetrics())
    const socket = io('http://localhost:5050')

    socket.on('connect', () => {
      console.log('Connected to Flask')
    })

    socket.on('metric_update', (data) => {
      dispatch(addMetric(data))
    })

    socket.on('inference_update', (data) => {
      setInference(data)
    })

    socket.on('imu_update', (data) => {
      setImu(data)
    })

    return () => {
      socket.disconnect()
    }
  }, [dispatch])

  return (
    <div style={{ padding: '2rem' }}>
      <h1>ML Experiment Dashboard</h1>
      <h2>Live Training Metrics</h2>
      {Object.entries(experimentGroups).map(([expId, points]) => (
        <div key={expId} style={{ marginBottom: '2rem' }}>
          <h3>{expId}</h3>
          <LineChart width={700} height={300} data={points}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="epoch" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="loss" stroke="#ff0000" dot={false} />
            <Line type="monotone" dataKey="accuracy" stroke="#00ff00" dot={false} />
          </LineChart>
        </div>
      ))}
      <div style={{ marginTop: '2rem' }}>
        <h2>Experiment Summary</h2>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ccc', padding: '0.5rem' }}>Experiment</th>
              <th style={{ border: '1px solid #ccc', padding: '0.5rem' }}>Last Epoch</th>
              <th style={{ border: '1px solid #ccc', padding: '0.5rem' }}>Loss</th>
              <th style={{ border: '1px solid #ccc', padding: '0.5rem' }}>Accuracy</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(experimentGroups).map(([expId, points]) => {
              const last = points[points.length - 1]
              return (
                <tr key={expId}>
                  <td style={{ border: '1px solid #ccc', padding: '0.5rem' }}>{expId}</td>
                  <td style={{ border: '1px solid #ccc', padding: '0.5rem' }}>{last.epoch}</td>
                  <td style={{ border: '1px solid #ccc', padding: '0.5rem' }}>{last.loss}</td>
                  <td style={{ border: '1px solid #ccc', padding: '0.5rem' }}>{last.accuracy}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {/*<div style={{ marginTop: '2rem' }}>
        {metrics.map((m, i) => (
          <div key={i}>
            Epoch {m.epoch} — Loss: {m.loss} — Accuracy: {m.accuracy}
          </div>
        ))}
      </div>*/}
      {inference && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
          <h2>Pi Inference Node</h2>
          <p>Prediction: {inference.prediction}</p>
          <p>Inference Latency: {inference.latency_ms}ms</p>
          <p>CPU Temperature: {inference.cpu_temp}°C</p>
        </div>
      )}
      {imu && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
          <h2>IMU Sensor</h2>
          <p>Accelerometer (g): X={imu.accel_x} Y={imu.accel_y} Z={imu.accel_z}</p>
          <p>Gyroscope (°/s): X={imu.gyro_x} Y={imu.gyro_y} Z={imu.gyro_z}</p>
        </div>
      )}
    </div>
  )
}
