import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Metric {
  experiment_id: string
  epoch: number
  loss: number
  accuracy: number
}

interface MetricsState {
  data: Metric[]
}

const initialState: MetricsState = {
  data: []
}

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    addMetric: (state, action: PayloadAction<Metric>) => {
      state.data.push(action.payload)
    },
    clearMetrics: (state) => {
      state.data = []
    }
  }
})

export const { addMetric, clearMetrics } = metricsSlice.actions
export default metricsSlice.reducer
