import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1/",
});

export const createPayout = (data) => {
  return API.post("payouts", data, {
    headers: {
      "Idempotency-Key": crypto.randomUUID(),
    },
  });
};

export const getPayout = (id) => {
  return API.get(`payouts/${id}`);
};