// import { useState } from "react";
// import { createPayout, getPayout } from "./api";

// import { useState, useEffect } from "react";
// import axios from "axios";



// function App() {
//   const [amount, setAmount] = useState("");
//   const [payoutId, setPayoutId] = useState(null);
//   const [status, setStatus] = useState(null);

//   const [balance, setBalance] = useState(0);
//   const [payouts, setPayouts] = useState([]);

//   const handleCreate = async () => {
//     try {
//       const res = await createPayout({
//         merchant_id: 9,
//         amount_paise: parseInt(amount),
//         bank_account_id: 1,
//       });

//       setPayoutId(res.data.id);
//       setStatus(res.data.status);
//     } catch (err) {
//       alert(err.response?.data?.error || "Error");
//     }
//   };

//   const handleCheck = async () => {
//     if (!payoutId) return;

//     const res = await getPayout(payoutId);
//     setStatus(res.data.status);
//   };

//   const fetchBalance = async () => {
//   const res = await axios.get(
//     "http://127.0.0.1:8000/api/v1/merchant/9/balance"
//   );
//   setBalance(res.data.balance);
//   };

//   const fetchPayouts = async () => {
//   const res = await axios.get(
//     "http://127.0.0.1:8000/api/v1/merchant/9/payouts"
//   );
//   setPayouts(res.data);
//   };



//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-100">
//       <div className="bg-white p-6 rounded shadow w-96">
//         <h1 className="text-xl font-bold mb-4">Payout Dashboard</h1>

//         <input
//           type="number"
//           placeholder="Amount (paise)"
//           className="border p-2 w-full mb-4"
//           value={amount}
//           onChange={(e) => setAmount(e.target.value)}
//         />

//         <button
//           onClick={handleCreate}
//           className="bg-blue-500 text-white w-full py-2 rounded mb-4"
//         >
//           Create Payout
//         </button>

//         {payoutId && (
//           <>
//             <p><b>ID:</b> {payoutId}</p>
//             <p><b>Status:</b> {status}</p>

//             <button
//               onClick={handleCheck}
//               className="bg-green-500 text-white w-full py-2 rounded mt-3"
//             >
//               Refresh Status
//             </button>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;

import { useState, useEffect } from "react";
import axios from "axios";

// ✅ AUTO SWITCH (local vs production)
const API =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000/api/v1"; // fallback for local

function App() {
  const [amount, setAmount] = useState("");
  const [payoutId, setPayoutId] = useState(null);
  const [status, setStatus] = useState(null);

  const [balance, setBalance] = useState(0);
  const [payouts, setPayouts] = useState([]);

  const MERCHANT_ID = 1;

  // 🔹 Create payout
  const handleCreate = async () => {
    try {
      const res = await axios.post(
        `${API}/payouts`,
        {
          merchant_id: MERCHANT_ID,
          amount_paise: parseInt(amount),
        },
        {
          headers: {
            "Content-Type": "application/json",
            "Idempotency-Key": crypto.randomUUID(),
          },
        }
      );

      setPayoutId(res.data.id);
      setStatus(res.data.status);

      await fetchBalance();
      await fetchPayouts();
    } catch (err) {
      alert(err.response?.data?.error || "Error");
    }
  };

  // 🔹 Manual status check
  const handleCheck = async () => {
    if (!payoutId) return;

    const res = await axios.get(`${API}/payouts/${payoutId}`);
    setStatus(res.data.status);
  };

  // 🔹 Fetch balance
  const fetchBalance = async () => {
    const res = await axios.get(
      `${API}/merchant/${MERCHANT_ID}/balance`
    );
    setBalance(res.data.balance);
  };

  // 🔹 Fetch payout history
  const fetchPayouts = async () => {
    const res = await axios.get(
      `${API}/merchant/${MERCHANT_ID}/payouts`
    );
    setPayouts(res.data);
  };

  // 🔹 Load on start
  useEffect(() => {
    fetchBalance();
    fetchPayouts();
  }, []);

  // 🔹 Auto refresh
  useEffect(() => {
    if (!payoutId) return;

    const interval = setInterval(async () => {
      const res = await axios.get(`${API}/payouts/${payoutId}`);
      setStatus(res.data.status);

      if (
        res.data.status === "completed" ||
        res.data.status === "failed"
      ) {
        clearInterval(interval);
        fetchBalance();
        fetchPayouts();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [payoutId]);

  // 🔹 Status color
  const getColor = (status) => {
    if (status === "completed") return "green";
    if (status === "failed") return "red";
    return "orange";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-6 rounded shadow w-96">

        <h1 className="text-xl font-bold mb-2">Payout Dashboard</h1>

        <p className="mb-3">
          <b>Balance:</b> ₹ {balance / 100}
        </p>

        <input
          type="number"
          placeholder="Amount (paise)"
          className="border p-2 w-full mb-4"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />

        <button
          onClick={handleCreate}
          className="bg-blue-500 text-white w-full py-2 rounded mb-4"
        >
          Create Payout
        </button>

        {payoutId && (
          <>
            <p><b>ID:</b> {payoutId}</p>
            <p>
              <b>Status:</b>{" "}
              <span style={{ color: getColor(status) }}>
                {status}
              </span>
            </p>

            <button
              onClick={handleCheck}
              className="bg-green-500 text-white w-full py-2 rounded mt-3"
            >
              Refresh Status
            </button>
          </>
        )}

        <h3 className="mt-6 font-bold">Payout History</h3>

        <table className="w-full mt-2 text-sm border">
          <thead>
            <tr className="bg-gray-200">
              <th>ID</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {payouts.map((p) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>₹ {p.amount / 100}</td>
                <td style={{ color: getColor(p.status) }}>
                  {p.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>
    </div>
  );
}

export default App;