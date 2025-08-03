import React, { useState, useEffect, useContext } from 'react';
import { Table, Form, Button, Modal, message, Select, Switch, TimePicker, InputNumber } from 'antd';
import axios from 'axios';
import { userContext } from "../UserContext/UserContext";
import moment from 'moment';

const daysOfWeek = [
    { id: 0, name: 'Monday' },
    { id: 1, name: 'Tuesday' },
    { id: 2, name: 'Wednesday' },
    { id: 3, name: 'Thursday' },
    { id: 4, name: 'Friday' },
    { id: 5, name: 'Saturday' },
    { id: 6, name: 'Sunday' },
];

const DoctorScheduleManage = () => {
    const { userToken } = useContext(userContext);
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
        fetchSchedules();
    }, []);

    const fetchSchedules = async () => {
        try {
            setLoading(true);
            const response = await axios.get('https://grackle-notable-hardly.ngrok-free.app/api/appointments/doctor/schedule/', {
                headers: {
                    Authorization: `Bearer ${userToken}`,
                },
            });
            
            // Improved response handling
            let schedulesData = [];
            if (Array.isArray(response.data)) {
                schedulesData = response.data;
            } else if (response.data?.results) {
                schedulesData = response.data.results;
            } else if (response.data?.schedules) {
                schedulesData = response.data.schedules;
            } else if (response.data) {
                // Handle case where response.data is the array itself
                schedulesData = Object.values(response.data);
            }
            
            // Convert time strings to moment objects and ensure all fields exist
            const formattedSchedules = schedulesData.map(schedule => ({
                id: schedule.id || schedule._id,
                day_of_week: schedule.day_of_week,
                is_working_day: schedule.is_working_day !== false,
                start_time: schedule.start_time ? moment(schedule.start_time, 'HH:mm:ss') : null,
                end_time: schedule.end_time ? moment(schedule.end_time, 'HH:mm:ss') : null,
                appointment_duration: schedule.appointment_duration || 30
            }));
            
            setSchedules(formattedSchedules);
        } catch (error) {
            console.error('Error fetching schedules:', error);
            message.error(error.response?.data?.message || 'Failed to fetch schedules');
        } finally {
            setLoading(false);
        }
    };

    const handleAddSchedule = () => {
        form.resetFields();
        setIsModalVisible(true);
    };

    const handleSubmit = async (values) => {
        try {
            setLoading(true);
            const postData = {
                day_of_week: values.day_of_week,
                is_working_day: values.is_working_day !== false,
                start_time: values.start_time ? values.start_time.format('HH:mm:ss') : '09:00:00',
                end_time: values.end_time ? values.end_time.format('HH:mm:ss') : '17:00:00',
                appointment_duration: values.appointment_duration || 30,
            };

            const response = await axios.post(
                'https://grackle-notable-hardly.ngrok-free.app/api/appointments/doctor/schedule/', 
                postData,
                {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            
            // Handle different response formats
            const newSchedule = response.data?.data || response.data;
            
            if (newSchedule) {
                // Add the new schedule to the existing schedules
                setSchedules(prev => [
                    ...prev,
                    {
                        id: newSchedule.id || newSchedule._id,
                        day_of_week: newSchedule.day_of_week,
                        is_working_day: newSchedule.is_working_day !== false,
                        start_time: newSchedule.start_time ? moment(newSchedule.start_time, 'HH:mm:ss') : null,
                        end_time: newSchedule.end_time ? moment(newSchedule.end_time, 'HH:mm:ss') : null,
                        appointment_duration: newSchedule.appointment_duration || 30
                    }
                ]);
                
                message.success('Schedule added successfully');
                setIsModalVisible(false);
            } else {
                // If response doesn't contain the new schedule, refetch
                message.success('Schedule added successfully. Refreshing...');
                fetchSchedules();
                setIsModalVisible(false);
            }
        } catch (error) {
            console.error('Error adding schedule:', {
                status: error.response?.status,
                data: error.response?.data,
                config: error.config,
            });
            
            if (error.response?.data) {
                const errorMessages = [];
                for (const [field, errors] of Object.entries(error.response.data)) {
                    errorMessages.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
                }
                message.error(`Validation errors:\n${errorMessages.join('\n')}`);
            } else {
                message.error(error.message || 'Failed to add schedule');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        try {
            setLoading(true);
            await axios.delete(
                `https://grackle-notable-hardly.ngrok-free.app/api/appointments/doctor/schedule/${id}/`, 
                {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                    },
                }
            );
            
            // Remove the deleted schedule from state
            setSchedules(prev => prev.filter(schedule => schedule.id !== id));
            message.success('Schedule deleted successfully');
        } catch (error) {
            console.error('Error deleting schedule:', error);
            message.error(
                error.response?.data?.message || 
                error.response?.data?.detail || 
                'Failed to delete schedule'
            );
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        {
            title: 'Day',
            dataIndex: 'day_of_week',
            key: 'day_of_week',
            render: (day) => daysOfWeek.find(d => d.id === day)?.name || day,
        },
        {
            title: 'Working Day',
            dataIndex: 'is_working_day',
            key: 'is_working_day',
            render: (isWorking) => (isWorking ? 'Yes' : 'No'),
        },
        {
            title: 'Start Time',
            dataIndex: 'start_time',
            key: 'start_time',
            render: (time) => time ? time.format('HH:mm') : '-',
        },
        {
            title: 'End Time',
            dataIndex: 'end_time',
            key: 'end_time',
            render: (time) => time ? time.format('HH:mm') : '-',
        },
        {
            title: 'Duration (min)',
            dataIndex: 'appointment_duration',
            key: 'appointment_duration',
            render: (duration) => duration || '-',
        },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Button 
                    danger 
                    onClick={() => handleDelete(record.id)}
                    disabled={loading}
                >
                    Delete
                </Button>
            ),
        },
    ];

    return (
        <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                <h2>Doctor Schedule Management</h2>
                <Button 
                    type="primary" 
                    onClick={handleAddSchedule}
                    loading={loading}
                >
                    Add Schedule
                </Button>
            </div>

            <Table
                columns={columns}
                dataSource={schedules}
                rowKey="id"
                loading={loading}
                pagination={false}
                bordered
            />

            <Modal
                title="Add Schedule"
                open={isModalVisible}
                onCancel={() => setIsModalVisible(false)}
                onOk={() => form.submit()}
                okText="Save"
                cancelText="Cancel"
                confirmLoading={loading}
                destroyOnClose
            >
                <Form 
                    form={form} 
                    onFinish={handleSubmit} 
                    layout="vertical"
                    initialValues={{
                        is_working_day: true,
                        appointment_duration: 30
                    }}
                >
                    <Form.Item
                        name="day_of_week"
                        label="Day of Week"
                        rules={[{ 
                            required: true, 
                            message: 'Please select a day' 
                        }]}
                    >
                        <Select 
                            placeholder="Select a day"
                            optionFilterProp="children"
                        >
                            {daysOfWeek.map(day => (
                                <Select.Option 
                                    key={day.id} 
                                    value={day.id}
                                >
                                    {day.name}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="is_working_day"
                        label="Is Working Day"
                        valuePropName="checked"
                    >
                        <Switch />
                    </Form.Item>

                    <Form.Item
                        noStyle
                        shouldUpdate={(prevValues, currentValues) =>
                            prevValues.is_working_day !== currentValues.is_working_day
                        }
                    >
                        {({ getFieldValue }) =>
                            getFieldValue('is_working_day') ? (
                                <>
                                    <Form.Item
                                        name="start_time"
                                        label="Start Time"
                                        rules={[{ 
                                            required: true, 
                                            message: 'Please enter start time' 
                                        }]}
                                    >
                                        <TimePicker 
                                            format="HH:mm" 
                                            style={{ width: '100%' }} 
                                            minuteStep={15}
                                            showNow={false}
                                        />
                                    </Form.Item>

                                    <Form.Item
                                        name="end_time"
                                        label="End Time"
                                        rules={[
                                            {
                                                required: true,
                                                message: 'Please enter end time',
                                            },
                                            {
                                                validator: (_, value) => {
                                                    const startTime = form.getFieldValue('start_time');

                                                    if (!moment.isMoment(value) || !moment.isMoment(startTime)) {
                                                        return Promise.resolve();
                                                    }

                                                    if (value.isSameOrBefore(startTime)) {
                                                        return Promise.reject(new Error('End time must be after start time'));
                                                    }

                                                    return Promise.resolve();
                                                },
                                            },
                                        ]}
                                    >
                                        <TimePicker
                                            format="HH:mm"
                                            style={{ width: '100%' }}
                                            minuteStep={15}
                                            showNow={false}
                                        />
                                    </Form.Item>

                                    <Form.Item
                                        name="appointment_duration"
                                        label="Appointment Duration (minutes)"
                                        rules={[{ 
                                            required: true, 
                                            message: 'Please enter duration between 10-120 minutes',
                                            type: 'number',
                                            min: 10,
                                            max: 120
                                        }]}
                                    >
                                        <InputNumber 
                                            min={10} 
                                            max={120} 
                                            style={{ width: '100%' }} 
                                        />
                                    </Form.Item>
                                </>
                            ) : null
                        }
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default DoctorScheduleManage;