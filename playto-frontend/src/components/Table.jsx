export default function Table({ columns, data }) {
  return (
    <div className="bg-white rounded shadow overflow-auto">
      <table className="w-full text-sm">
        
        {/* Header */}
        <thead className="bg-gray-200 text-gray-700">
          <tr>
            {columns.map((col, index) => (
              <th key={index} className="p-3 text-left">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>

        {/* Body */}
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="text-center p-4 text-gray-500">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr
                key={i}
                className="border-b hover:bg-gray-100 transition"
              >
                {columns.map((col, j) => (
                  <td key={j} className="p-3">
                    {col.render ? col.render(row) : row[col.accessor]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}