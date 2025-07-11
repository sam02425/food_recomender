import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import CustomerIdentification from '../CustomerIdentification';

describe('CustomerIdentification', () => {
  it('submits name and phone', async () => {
    const onCustomerIdentified = jest.fn();
    render(<CustomerIdentification onCustomerIdentified={onCustomerIdentified} />);

    // Enter name
    const nameInput = screen.getByLabelText(/name/i);
    fireEvent.change(nameInput, { target: { value: 'Test User' } });

    // Enter phone
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });

    // Submit form
    const submitButton = screen.getByRole('button', { name: /submit|identify|continue/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(onCustomerIdentified).toHaveBeenCalled();
    });
  });
});