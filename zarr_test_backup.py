import zarr
import pandas as pd
import numpy as np
df = pd.DataFrame
import os



class ZarrHelper:
    def __init__(self, default_dtype = float):
        self._default_dtype = default_dtype

    @staticmethod
    def get_appending_time(ts, appending_unit=60 * 60 * 24 * 5):
        return (ts - 1) // appending_unit * appending_unit + appending_unit

    def write_lv2(self, data, path, chunks = (720, 30)):
        ts_list = data.index.values.astype(np.int64)
        trim = data.columns.values.astype('<U20')
        value = data.values.astype(self._default_dtype)

        if not isinstance(chunks, bool):
            with zarr.open(path, 'w') as zr:
                zr.create_dataset('timestamp', data = ts_list, shape = (None, ), chunks = (chunks[0], ), dtype = np.int64)
                zr.create_dataset('value', data = value, shape = (None, None), chunks = chunks, dtype = self._default_dtype, fillvalue = np.nan)
                zr.create_dataset('trim', data = trim, shape = (None, ), chunks = (chunks[1], ))
        else:
            with zarr.open(path, 'w') as zr:
                zr.create_dataset('timestamp', data = ts_list, shape = (None, ), chunks = chunks, dtype = np.int64)
                zr.create_dataset('value', data = value, shape = (None, None), chunks = chunks, dtype = self._default_dtype, fillvalue = np.nan)
                zr.create_dataset('trim', data = trim, shape = (None, ), chunks = chunks)
        return True

    def append_lv2(self, data, path, chunks = (720, 30)):
        if not os.path.exists(path):
            self.write_lv2(data, path, chunks)
            return True

        ts_list = data.index.values.astype(np.int64)
        trim = data.columns.values.astype(str)

        # old ts_list and trim
        with zarr.open(path, 'r') as zr:
            old_ts = zr['timestamp'][-1]
            old_trim = zr['trim'][:]

        # check if new timestamp
        new_ts_list = ts_list[ts_list > old_ts]

        #check if new trim
        new_trim = list(set(trim) - set(old_trim))

        new_ts_shape = new_ts_list.shape[0]
        new_tr_shape = len(new_trim)

        if (new_ts_shape > 0) & (new_tr_shape > 0):
            with zarr.open(path, 'a') as zr:
                full_ts_shape = zr['timestamp'].shape[0] + new_ts_shape
                full_tr_shape = old_trim.shape[0] + new_tr_shape
                zr['timestamp'].resize((full_ts_shape, ))
                zr['timestamp'][-new_ts_shape:] = new_ts_list

                zr['trim'].resize((full_tr_shape, ))
                zr['trim'][-new_tr_shape:] = new_trim

                full_trim = list(old_trim) + new_trim
                value = data.reindex(new_ts_list, axis = 0).reindex(full_trim, axis = 1).values
                zr['value'].resize((full_ts_shape, full_tr_shape))
                zr['value'][-new_ts_shape:] = value

        elif new_ts_shape > 0:
            with zarr.open(path, 'a') as zr:
                full_ts_shape = zr['timestamp'].shape[0] + new_ts_shape
                zr['timestamp'].resize((full_ts_shape, ))
                zr['timestamp'][-new_ts_shape:] = new_ts_list

                value = data.reindex(new_ts_list, axis = 0).reindex(old_trim, axis = 1).values
                zr['value'].resize((full_ts_shape, old_trim.shape[0]))
                zr['value'][-new_ts_shape:] = value
        # Should not Happend
        elif new_tr_shape > 0:
            raise ValueError('Datetime not updated but only trim updated, new trim: {}\npath: {}'.format(new_trim
                                                                                                         , path))
        return True


    def write_lv2_series(self, data, path, chunks = (720, 30)):
        ts = np.int64(data.name)
        trim = data.index.values.astype(str)
        value = data.values.astype(self._default_dtype)

        if not isinstance(chunks, bool):
            with zarr.open(path, 'w') as zr:
                zr.create_dataset('timestamp', data = [ts], shape = (None, ), chunks = (chunks[0], ), dtype = np.int64)
                zr.create_dataset('value', data = [value], shape = (None, None), chunks = chunks, dtype = self._default_dtype, fillvalue = np.nan)
                zr.create_dataset('trim', data = trim, shape = (None, ), chunks = (chunks[1], ))
        else:
            with zarr.open(path, 'w') as zr:
                zr.create_dataset('timestamp', data = [ts], shape = (None, ), chunks = False, dtype = np.int64)
                zr.create_dataset('value', data = [value], shape = (None, None), chunks = False, dtype = self._default_dtype, fillvalue = np.nan)
                zr.create_dataset('trim', data = trim, shape = (None, ), chunks = False)

        return True

    def append_lv2_series(self, data, path, chunks = (720, 30)):
        if not os.path.exists(path):
            self.write_lv2_series(data, path, chunks)
            return True

        ts = np.int64(data.name)
        trim = data.index.values.astype(str)

        with zarr.open(path, 'r') as zr:
            old_ts = zr['timestamp'][-1]
            old_trim = zr['trim'][:]

        if ts <= old_ts:
            print ('current ts less than cached ts, {} <= {}'.format(ts, old_ts))
            return False

        new_trim = list(set(trim) - set(old_trim))
        new_tr_shape = len(new_trim)

        if len(new_trim) > 0:
            with zarr.open(path, 'a') as zr:
                full_tr_shape = old_trim.shape[0] + new_tr_shape
                full_ts_shape = zr['timestamp'].shape[0] + 1

                zr['timestamp'].resize((full_ts_shape, ))
                zr['timestamp'][-1] = ts

                zr['trim'].resize((full_tr_shape, ))
                zr['trim'][-new_tr_shape:] = new_trim

                full_trim = list(old_trim) + new_trim
                value = data.reindex(full_trim).values
                zr['value'].resize((full_ts_shape, full_tr_shape))
                zr['value'][-1] = value

        else:
            with zarr.open(path, 'a') as zr:
                full_ts_shape = zr['timestamp'].shape[0] + 1
                zr['timestamp'].resize((full_ts_shape, ))
                zr['timestamp'][-1] = ts

                value = data.reindex(old_trim).values
                zr['value'].resize((full_ts_shape, zr['value'].shape[1]))
                zr['value'][-1] = value

        return True

    def _read_lv2(self, path, start_ts = None, end_ts = None):
        with zarr.open(path, 'r') as zr:
            ts_list = zr['timestamp'][:]

        if isinstance(start_ts, type(None)):
            start_ts = ts_list[0]
        else:
            start_ts = max(ts_list[0], start_ts)

        if isinstance(end_ts, type(None)):
            end_ts = ts_list[-1]
            if end_ts == 0:
                end_ts = ts_list[-2]
        else:
            end_ts = min(ts_list[-1], end_ts)

        start_idx = ts_list.searchsorted(start_ts)
        end_idx = ts_list.searchsorted(end_ts)

        with zarr.open(path, 'r') as zr:
            ts_list = zr['timestamp'][start_idx:end_idx+1]
            value = zr['value'][start_idx:end_idx+1]
            trim = zr['trim'][:]

        return self.sanity_check(value, ts_list, trim)

    def read_lv2(self, path, start_ts, end_ts, appending_unit=60 * 60 * 24 * 5):
        at_start = self.get_appending_time(start_ts)
        at_end = self.get_appending_time(end_ts)

        at_list = range(at_start, at_end + 1, appending_unit)

        data = df()
        for at in at_list:
            target_path = os.path.join(path, str(at))
            target_start = max(start_ts, at_start)
            target_end = min(at_end, end_ts)
            data = pd.concat([data, self._read_lv2(target_path, target_start, target_end)])

        return data

    def read_lv2_ts_list(self, path, ts_list):
        with zarr.open(path, 'r') as zr:
            cache_ts_list = zr['timestamp'][:]

        ti_list = cache_ts_list.searchsorted(ts_list)
        ti_list = ti_list[cache_ts_list[ti_list] == ts_list]

        with zarr.open(path, 'r') as zr:
            ts_list = zr['timestamp'][ti_list]
            value = zr['value'][ti_list]
            trim = zr['trim'][:]

        return self.sanity_check(value, ts_list, trim)

    def sanity_check(self, value, ts_list, trim):
        ti_shape = min(value.shape[0], ts_list.shape[0])
        ii_shape = min(value.shape[1], trim.shape[0])
        value = value[:ti_shape, :ii_shape]
        ts_list = ts_list[:ti_shape]
        trim = trim[:ii_shape]
        return df(value, ts_list, trim)