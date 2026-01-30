import apiClient from '../axios';
import { AxiosResponse } from 'axios';
import { PaginationParams, PaginatedResponse } from '../../types/employee';

export class BaseAPIService<T> {
  protected endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  /**
   * Get all items with pagination
   */
  async getAll(params?: PaginationParams & Record<string, any>): Promise<PaginatedResponse<T>> {
    const response: AxiosResponse<PaginatedResponse<T>> = await apiClient.get(
      this.endpoint,
      { params }
    );
    return response.data;
  }

  /**
   * Get single item by ID
   */
  async getById(id: string): Promise<T> {
    const response: AxiosResponse<T> = await apiClient.get(
      `${this.endpoint}/${id}` 
    );
    return response.data;
  }

  /**
   * Create new item
   */
  async create<TCreate = Partial<T>>(data: TCreate): Promise<T> {
    const response: AxiosResponse<T> = await apiClient.post(
      this.endpoint,
      data
    );
    return response.data;
  }

  /**
   * Update existing item
   */
  async update<TUpdate = Partial<T>>(id: string, data: TUpdate): Promise<T> {
    const response: AxiosResponse<T> = await apiClient.put(
      `${this.endpoint}/${id}`,
      data
    );
    return response.data;
  }

  /**
   * Partially update item
   */
  async patch<TPatch = Partial<T>>(id: string, data: TPatch): Promise<T> {
    const response: AxiosResponse<T> = await apiClient.patch(
      `${this.endpoint}/${id}`,
      data
    );
    return response.data;
  }

  /**
   * Delete item
   */
  async delete(id: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`${this.endpoint}/${id}`);
    return response.data;
  }
}
