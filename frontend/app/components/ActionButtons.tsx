export const ActionButtons = ({ isFetching, handleToggleFetching, storeCurrentReading, loadRecentReadings, hideRecentReadings, readingsVisible }) => (
    <div className="mt-4 flex flex-row space-x-2">
      <button className="bg-blue-500 text-white py-2 px-4 rounded" onClick={handleToggleFetching}>
        {isFetching ? 'Pause Fetching' : 'Resume Fetching'}
      </button>
      <button className="bg-green-500 text-white py-2 px-4 rounded" onClick={storeCurrentReading}>
        Store Current Reading
      </button>
      <button className="bg-green-500 text-white py-2 px-4 rounded" onClick={loadRecentReadings}>
        Show Recent Readings
      </button>
      {readingsVisible && (
        <button className="bg-red-500 text-white py-2 px-4 rounded" onClick={hideRecentReadings}>
          Hide Recent Readings
        </button>
      )}
    </div>
  );